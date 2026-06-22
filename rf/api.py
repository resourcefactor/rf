import frappe


def boot_session(bootinfo):
	"""Attach RF Settings to bootinfo so the desk JS can read branding config without an extra API call."""
	if frappe.session["user"] != "Guest":
		bootinfo.rf_settings = frappe.get_doc("RF Settings", "RF Settings").as_dict()


_HIDE_HELP_LABELS = {"About", "Frappe Support"}


def extend_bootinfo(bootinfo):
	"""Runs after full bootinfo (including desk_settings) is assembled."""
	if frappe.session["user"] == "Guest":
		return

	_filter_notes_by_company(bootinfo)
	_apply_rf_settings(bootinfo)


def _get_label(item):
	return item.get("item_label") if isinstance(item, dict) else getattr(item, "item_label", "")


def _apply_rf_settings(bootinfo):
	rf = bootinfo.get("rf_settings") or {}
	if not rf.get("hide_help_menu"):
		return

	navbar = bootinfo.get("navbar_settings")
	if not navbar:
		return

	if isinstance(navbar, dict):
		navbar["help_dropdown"] = [
			item for item in (navbar.get("help_dropdown") or [])
			if _get_label(item) not in _HIDE_HELP_LABELS
		]
	else:
		navbar.help_dropdown = [
			item for item in (navbar.help_dropdown or [])
			if _get_label(item) not in _HIDE_HELP_LABELS
		]



def _filter_notes_by_company(bootinfo):
	if not bootinfo.get("notes"):
		return

	user = frappe.session.user
	user_companies = frappe.db.get_all(
		"User Permission",
		filters={"user": user, "allow": "Company"},
		pluck="for_value",
	)

	filtered = []
	for note in bootinfo.notes:
		companies = frappe.db.get_all(
			"Note Restrict Company",
			filters={"parent": note.name},
			pluck="company",
		)
		if not companies:
			filtered.append(note)
		elif any(c in user_companies for c in companies):
			filtered.append(note)

	bootinfo.notes = filtered


def get_website_context(context):
	"""Override the login page logo for guest users if login_page_logo is configured."""
	if frappe.session.user != "Guest":
		return context
	login_logo_url = frappe.conf.get("login_logo_url")
	if login_logo_url:
		context["app_logo_url"] = login_logo_url
	return context


@frappe.whitelist(allow_guest=True)
def get_login_logo_url():
	"""Return login logo URL from site config (used by whitelabel_web.js on the login page)."""
	login_logo_url = frappe.conf.get("login_logo_url")
	return {"login_logo_url": login_logo_url if login_logo_url else None}


@frappe.whitelist()
def ignore_update_popup():
	if not frappe.db.get_single_value("RF Settings", "disable_new_update_popup"):
		from frappe.utils.change_log import show_update_popup

		show_update_popup()
