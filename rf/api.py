from __future__ import unicode_literals
import frappe
import re
import json
from frappe.utils import floor, flt, today, cint
from frappe import _

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
	rename_erpnext_workspaces()

def boot_session(bootinfo):
	"""boot session - send website info if guest"""
	if frappe.session['user']!='Guest':
		bootinfo.whitelabel_setting = frappe.get_doc("Whitelabel Setting","Whitelabel Setting")

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
	"""Rename ERPNext Workspaces to ERP Workspaces and remove duplicates"""
	workspace_renames = {
		"ERPNext Integrations": "ERP Integrations",
		"ERPNext Settings": "ERP Settings"
	}

	for old_name, new_name in workspace_renames.items():
		try:
			print(f"\n=== Processing workspace: {old_name} ===")

			# Check if new workspace exists
			new_exists = frappe.db.exists("Workspace", new_name)
			old_exists = frappe.db.exists("Workspace", old_name)

			print(f"Old workspace '{old_name}' exists: {old_exists}")
			print(f"New workspace '{new_name}' exists: {new_exists}")

			if old_exists and not new_exists:
				# Only old exists - rename it
				print(f"Renaming '{old_name}' to '{new_name}'")
				frappe.rename_doc("Workspace", old_name, new_name, force=True, merge=False)
				frappe.db.commit()
				print(f"Successfully renamed workspace")
			elif old_exists and new_exists:
				# Both exist - this is the duplicate issue
				print(f"Both workspaces exist - deleting old workspace '{old_name}'")

				# First, update all references to point to new workspace
				shortcuts = frappe.get_all("Workspace Shortcut",
					filters={"link_to": old_name},
					fields=["name", "parent"])
				for shortcut in shortcuts:
					frappe.db.set_value("Workspace Shortcut", shortcut.name, "link_to", new_name)
					print(f"Updated shortcut in {shortcut.parent}")

				links = frappe.get_all("Workspace Link",
					filters={"link_to": old_name},
					fields=["name", "parent"])
				for link in links:
					frappe.db.set_value("Workspace Link", link.name, "link_to", new_name)
					print(f"Updated link in {link.parent}")

				# Now delete the old workspace
				frappe.delete_doc("Workspace", old_name, force=True, ignore_permissions=True)
				frappe.db.commit()
				print(f"Deleted old workspace '{old_name}'")

			# Ensure the title field is correct on the new/renamed workspace
			if frappe.db.exists("Workspace", new_name):
				doc = frappe.get_doc("Workspace", new_name)
				if doc.title != new_name:
					print(f"Updating title from '{doc.title}' to '{new_name}'")
					doc.title = new_name
					doc.save(ignore_permissions=True)
					frappe.db.commit()

			print(f"=== Finished processing workspace ===\n")

		except Exception as e:
			print(f"ERROR processing workspace {old_name}: {str(e)}")
			import traceback
			traceback.print_exc()
			frappe.log_error(f"Workspace Rename Error: {old_name}", str(e))

	# Clear all caches to remove old workspace references
	print("Clearing all caches...")
	frappe.clear_cache()
	print("Workspace processing completed!")
