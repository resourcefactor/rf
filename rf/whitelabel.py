"""Idempotent white-label enforcement for the settings that have to live in the database.

Renames are not done here: they ship as `rf/translations/en.csv`, which migrate cannot touch.
This module covers what must be stored as data -- Navbar Settings help rows, System/Website
Settings toggles, CRM dropdown rows and onboarding text.

`apply_whitelabel` runs on `after_migrate` (after frappe has re-synced help rows, fixtures and
onboarding JSON), on `after_install` and on every RF Settings save. Each step writes only when a
value differs from its target, so a second run makes no writes.
"""

import frappe

BRAND_FALLBACK = "ERP"
# App names that are vendor defaults rather than something a site chose.
VENDOR_APP_NAMES = {"", "Frappe", "Frappe Framework", "ERPNext"}
TEXT_REPLACEMENTS = (("ERPNext", "ERP"), ("Frappe HR", "HR"), ("Frappe CRM", "CRM"))

# Standard help rows System Managers keep; every other standard row is hidden.
ADMIN_HELP_LABELS = {"System Health", "Keyboard Shortcuts"}
ADMIN_CONDITION = "frappe.user.has_role('System Manager')"

# FCRM Settings dropdown rows (by `name1`) that point at the vendor.
CRM_VENDOR_ITEMS = ("login_to_fc", "about")

RF_LOGO = "/assets/rf/images/rf_png.png"
RF_FAVICON = "/assets/rf/images/rf_ico.ico"
RF_SPLASH = "/assets/rf/images/rf_svg.svg"


def apply_whitelabel(settings=None):
	settings = settings or frappe.get_single("RF Settings")
	for step in (
		_apply_help_menu,
		_apply_system_settings,
		_apply_website_settings,
		_apply_crm_dropdown,
		_apply_onboarding,
	):
		try:
			step(settings)
		except Exception:
			# A vendor schema change must never break migrate; log and carry on.
			frappe.log_error(title=f"RF white-label: {step.__name__} failed")


def _brand_name(settings, current):
	"""The app name to store: RF Settings' explicit name, else keep a site's own choice."""
	explicit = (settings.whitelabel_app_name or "").strip()
	if explicit:
		return explicit
	if (current or "").strip() in VENDOR_APP_NAMES:
		return BRAND_FALLBACK
	return current


def _apply_help_menu(settings):
	navbar = frappe.get_single("Navbar Settings")
	changed = False
	for row in navbar.help_dropdown:
		# Only rows synced from hooks; a help link an admin added by hand is left alone.
		if not row.is_standard:
			continue
		if settings.hide_help_menu:
			if row.item_label in ADMIN_HELP_LABELS:
				target = {"hidden": 0, "condition": ADMIN_CONDITION}
			else:
				target = {"hidden": 1}
		else:
			target = {"hidden": 0}
			if row.condition == ADMIN_CONDITION:
				target["condition"] = None
		for field, value in target.items():
			if (row.get(field) or None) != (value or None):
				row.set(field, value)
				changed = True
	if changed:
		# save() invalidates the client_cache copy that sessions.py hands to the desk.
		navbar.save(ignore_permissions=True)


def _apply_system_settings(settings):
	doc = frappe.get_single("System Settings")
	target = {
		# Sidebar "Switch to Frappe CRM / Helpdesk" banners.
		"disable_product_suggestion": 1,
		# "Sent via ERPNext" email footer.
		"disable_standard_email_footer": 1,
		"app_name": _brand_name(settings, doc.app_name),
	}
	if settings.disable_new_update_popup:
		target["disable_system_update_notification"] = 1
		target["disable_change_log_notification"] = 1
	# save(), not set_single_value: these are read as frappe.defaults, which on_update syncs.
	save_if_changed(doc, target)


def _apply_website_settings(settings):
	doc = frappe.get_single("Website Settings")
	app_name = _brand_name(settings, doc.app_name)
	target = {"app_name": app_name}
	# Fill only empty values; a logo or footer a client configured is never overwritten.
	if not doc.footer_powered:
		target["footer_powered"] = app_name
	if not doc.app_logo:
		target["app_logo"] = RF_LOGO
	if not doc.favicon:
		target["favicon"] = RF_FAVICON
	if not doc.splash_image:
		target["splash_image"] = RF_SPLASH
	save_if_changed(doc, target)

	# The /desk apps screen reads only Navbar Settings for its top-left logo.
	navbar = frappe.get_single("Navbar Settings")
	if not navbar.app_logo and doc.app_logo:
		navbar.app_logo = doc.app_logo
		navbar.save(ignore_permissions=True)


def _apply_crm_dropdown(settings):
	if "crm" not in frappe.get_installed_apps() or not frappe.db.table_exists("CRM Dropdown Item"):
		return
	hidden = 1 if settings.hide_help_menu else 0
	rows = frappe.get_all(
		"CRM Dropdown Item",
		filters={
			"parent": "FCRM Settings",
			"parenttype": "FCRM Settings",
			"name1": ["in", CRM_VENDOR_ITEMS],
			"hidden": ["!=", hidden],
		},
		pluck="name",
	)
	for name in rows:
		# Direct row update: CRM's own sync keeps `hidden` on existing rows, and FCRM Settings
		# refuses to delete standard rows.
		frappe.db.set_value("CRM Dropdown Item", name, "hidden", hidden, update_modified=False)
	if rows:
		frappe.clear_document_cache("FCRM Settings", "FCRM Settings")


def _apply_onboarding(settings):
	"""Rebrand onboarding text with db.set_value, never doc.save(): on developer-mode sites a save
	exports the doc into the owning app's JSON, which every site on the bench then imports."""
	strip_videos = bool(settings.hide_help_menu)
	for doctype, text_fields, url_fields in (
		("Module Onboarding", ("title", "subtitle", "success_message"), ("documentation_url",)),
		("Onboarding Step", ("title", "description"), ("intro_video_url",)),
	):
		meta = frappe.get_meta(doctype)
		text_fields = [f for f in text_fields if meta.has_field(f)]
		url_fields = [f for f in url_fields if meta.has_field(f)] if strip_videos else []
		if not text_fields and not url_fields:
			continue
		for row in frappe.get_all(doctype, fields=["name", *text_fields, *url_fields]):
			values = {}
			for field in text_fields:
				new = _rebrand(row.get(field))
				if new != row.get(field):
					values[field] = new
			for field in url_fields:
				if row.get(field):
					values[field] = ""
			if values:
				frappe.db.set_value(doctype, row.name, values, update_modified=False)


def _rebrand(text):
	if not text:
		return text
	for old, new in TEXT_REPLACEMENTS:
		text = text.replace(old, new)
	return text


def save_if_changed(doc, values):
	"""Set `values` on `doc` and save it only if at least one of them differs."""
	changed = False
	for field, value in values.items():
		if doc.get(field) != value:
			doc.set(field, value)
			changed = True
	if changed:
		doc.save(ignore_permissions=True)
	return changed
