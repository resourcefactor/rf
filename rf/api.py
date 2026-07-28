from __future__ import unicode_literals
import frappe
import re
import json
from frappe.utils import floor, flt, today, cint
from frappe import _
from frappe.core.doctype.user_permission.user_permission import insert_user_perm

def setup_note_company_field():
	"""Ensure the 'Restrict to Companies' custom field exists on Note doctype."""
	if not frappe.db.exists("Custom Field", "Note-restrict_to_companies"):
		frappe.get_doc({
			"doctype": "Custom Field",
			"dt": "Note",
			"fieldname": "restrict_to_companies",
			"fieldtype": "Table MultiSelect",
			"label": "Restrict to Companies",
			"options": "Note Restrict Company",
			"insert_after": "expire_notification_on",
			"permlevel": 1,
			"description": "If set, popup only shows to users who have User Permission access to one of the listed companies. Leave empty to show to all users."
		}).insert(ignore_permissions=True)
		frappe.db.commit()


def whitelabel_patch():
	#delete erpnext welcome page
	frappe.delete_doc_if_exists('Page', 'welcome-to-erpnext', force=1)
	#update Welcome Blog Post
	if frappe.db.exists("Blog Post", "Welcome"):
		frappe.db.set_value("Blog Post","Welcome","content","")
	update_field_label()
	brand_name = frappe.get_hooks("brand_name")[0]
	update_onboard_details(brand_name)
	update_website_settings(brand_name)
	update_system_settings(brand_name)

def boot_session(bootinfo):
	"""boot session - send website info if guest"""
	if frappe.session['user'] != 'Guest':
		bootinfo.whitelabel_setting = frappe.get_doc("Whitelabel Setting", "Whitelabel Setting")


def extend_bootinfo(bootinfo):
	"""Runs after bootinfo.notes is set — filter notes by company restriction."""
	if frappe.session['user'] == 'Guest':
		return
	_filter_notes_by_company(bootinfo)


def _filter_notes_by_company(bootinfo):
	"""Filter login popup notes based on company restriction.

	If a Note has entries in 'restrict_to_companies', only users who have
	a User Permission for at least one of those companies will see the popup.
	Notes with no company restriction are shown to all users (default behavior).
	"""
	if not bootinfo.get("notes"):
		return

	user = frappe.session.user

	# Get all companies this user has explicit User Permission access to
	user_companies = frappe.db.get_all(
		"User Permission",
		filters={"user": user, "allow": "Company"},
		pluck="for_value"
	)

	filtered = []
	for note in bootinfo.notes:
		companies = frappe.db.get_all(
			"Note Restrict Company",
			filters={"parent": note.name},
			pluck="company"
		)
		if not companies:
			# No restriction set — show to all (preserves existing behavior)
			filtered.append(note)
		elif any(c in user_companies for c in companies):
			# User has permission for at least one of the restricted companies
			filtered.append(note)
		# else: company-restricted note, user has no matching User Permission — skip

	bootinfo.notes = filtered

def get_website_context(context):
	"""Override website context for login and other public pages"""
	# Only apply custom logo for Guest users (login page, signup, etc.)
	if frappe.session.user != "Guest":
		return context

	# Get the login logo URL from site config
	login_logo_url = frappe.conf.get("login_logo_url")

	if login_logo_url:
		# Override app_logo_url for public pages
		context["app_logo_url"] = login_logo_url
		frappe.logger().info(f"[Whitelabel] Setting public page logo: {login_logo_url}")

	return context

@frappe.whitelist(allow_guest=True)
def get_login_logo_url():
	"""Return the login logo URL from site config"""
	login_logo_url = frappe.conf.get("login_logo_url")
	return {
		"login_logo_url": login_logo_url if login_logo_url else None
	}

@frappe.whitelist()
def ignore_update_popup():
	if not frappe.db.get_single_value('Whitelabel Setting', 'disable_new_update_popup'):
		show_update_popup_update()

def update_field_label():
	"""Update label of section break in employee doctype"""
	frappe.db.sql("""Update `tabDocField` set label='OneHash' where fieldname='erpnext_user' and parent='Employee'""")

def update_website_settings(brand_name):
	frappe.db.set_value("Website Settings", "Website Settings", "app_name", brand_name)
	frappe.db.commit()

def update_system_settings(brand_name):
	frappe.db.set_value("System Settings", "System Settings", "otp_issuer_name", brand_name)
	frappe.db.commit()

def update_onboard_details(brand_name):
	update_onboard_module(brand_name)
	update_onboard_steps(brand_name)

def update_onboard_module(brand_name):
	onboard_module_details = frappe.get_all("Module Onboarding",filters={},fields=["name"])
	for row in onboard_module_details:
		doc = frappe.get_doc("Module Onboarding",row.name)
		doc.title = re.sub("ERPNext", brand_name, doc.title)
		doc.success_message = re.sub("ERPNext", brand_name, doc.success_message)
		doc.documentation_url = ""
		doc.flags.ignore_mandatory = True
		doc.save(ignore_permissions = True)

def update_onboard_steps(brand_name):
	onboard_steps_details = frappe.get_all("Onboarding Step",filters={},fields=["name"])
	for row in onboard_steps_details:
		doc = frappe.get_doc("Onboarding Step",row.name)
		if doc.title:
			doc.title = re.sub("ERPNext", brand_name, doc.title)
		if doc.description:
			doc.description = re.sub("ERPNext", brand_name, doc.description)
		doc.intro_video_url = ""
		if doc.title == "Introduction to Website":
			doc.video_url = ""
		doc.flags.ignore_mandatory = True
		doc.save(ignore_permissions = True)

@frappe.whitelist()
def show_update_popup_update():
	cache = frappe.cache()
	user  = frappe.session.user
	update_info = cache.get_value("update-info")
	if not update_info:
		return

	updates = json.loads(update_info)

	# Check if user is int the set of users to send update message to
	update_message = ""
	if cache.sismember("update-user-set", user):
		for update_type in updates:
			release_links = ""
			for app in updates[update_type]:
				app = frappe._dict(app)
				release_links += "<b>{title}</b>: <a href='https://github.com/{org_name}/{app_name}/releases/tag/v{available_version}'>v{available_version}</a><br>".format(
					available_version = app.available_version,
					org_name          = app.org_name,
					app_name          = app.app_name,
					title             = app.title
				)
			if release_links:
				message = _("New {} releases for the following apps are available").format(_(update_type))
				update_message += "<div class='new-version-log'>{0}<div class='new-version-links'>{1}</div></div>".format(message, release_links)

	if update_message:
		frappe.msgprint(update_message, title=_("New updates are available"), indicator='green')
		cache.srem("update-user-set", user)

def rename_erpnext_workspaces():
	"""Update ERPNext Workspace titles to ERP (keep document name unchanged)"""
	workspace_title_updates = {
		"ERPNext Integrations": "ERP Integrations",
		"ERPNext Settings": "ERP Settings"
	}

	for workspace_name, new_title in workspace_title_updates.items():
		try:
			print(f"\n=== Processing workspace: {workspace_name} ===")

			if frappe.db.exists("Workspace", workspace_name):
				# Get the workspace document
				doc = frappe.get_doc("Workspace", workspace_name)
				current_title = doc.title

				print(f"Workspace '{workspace_name}' found")
				print(f"Current title: '{current_title}'")
				print(f"New title: '{new_title}'")

				# Update the title field only (keep document name as is)
				if current_title != new_title:
					doc.title = new_title
					doc.save(ignore_permissions=True)
					frappe.db.commit()
					print(f"✓ Updated title successfully")
				else:
					print(f"✓ Title already correct")

				print(f"Document name remains: '{workspace_name}'")
			else:
				print(f"Workspace '{workspace_name}' not found, skipping")

			print(f"=== Finished processing workspace ===\n")

		except Exception as e:
			print(f"ERROR processing workspace {workspace_name}: {str(e)}")
			import traceback
			traceback.print_exc()
			frappe.log_error(f"Workspace Title Update Error: {workspace_name}", str(e))

	# Clear all caches to reflect title changes
	print("Clearing all caches...")
	frappe.clear_cache()
	print("Workspace title updates completed!")


@frappe.whitelist()
def get_user_permission_manager_data(user, allow, applicable_for=None, apply_to_all_doctypes=1):
	"""Return existing User Permission for_values for the given user+allow+scope.

	Used by the User Permission Manager page to pre-check the checkbox grid
	against what's already saved for this exact scope (same tuple that
	User Permission's own duplicate check uses, so the UI can never disagree
	with what the server considers a duplicate).
	"""
	frappe.only_for("System Manager")
	return frappe.get_all(
		"User Permission",
		filters={
			"user": user,
			"allow": allow,
			"applicable_for": applicable_for or None,
			"apply_to_all_doctypes": cint(apply_to_all_doctypes),
		},
		pluck="for_value",
	)


@frappe.whitelist()
def save_user_permission_manager_selection(
	user, allow, to_add, to_remove, applicable_for=None,
	apply_to_all_doctypes=1, hide_descendants=0, is_default=0,
):
	"""Bulk create/delete User Permission rows for one user+allow from a checkbox diff.

	Rows that fail validation (e.g. a duplicate default) are skipped rather than
	aborting the whole batch, so one bad row doesn't block the rest of the save.
	"""
	frappe.only_for("System Manager")

	if isinstance(to_add, str):
		to_add = json.loads(to_add)
	if isinstance(to_remove, str):
		to_remove = json.loads(to_remove)

	if cint(is_default) and len(to_add) > 1:
		frappe.throw(_("Is Default can only be applied when adding a single new permission."))

	added = []
	skipped = []
	for idx, for_value in enumerate(to_add):
		savepoint_name = f"user_perm_add_{idx}"
		frappe.db.savepoint(savepoint_name)
		try:
			insert_user_perm(
				user,
				allow,
				for_value,
				is_default=is_default,
				hide_descendants=hide_descendants,
				apply_to_all=cint(apply_to_all_doctypes) or None,
				applicable=applicable_for if not cint(apply_to_all_doctypes) else None,
			)
			added.append(for_value)
		except frappe.ValidationError as e:
			frappe.db.rollback(save_point=savepoint_name)
			frappe.clear_last_message()
			skipped.append({"value": for_value, "reason": str(e)})

	if to_remove:
		frappe.db.delete(
			"User Permission",
			{
				"user": user,
				"allow": allow,
				"for_value": ["in", to_remove],
				"applicable_for": applicable_for or None,
				"apply_to_all_doctypes": cint(apply_to_all_doctypes),
			},
		)
		frappe.clear_cache()

	frappe.logger().info(
		f"[UserPermissionManager] user={user} allow={allow} added={len(added)} "
		f"skipped={len(skipped)} removed={len(to_remove)}"
	)

	return {"added": len(added), "skipped": skipped, "removed": len(to_remove)}
