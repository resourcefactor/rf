# Copyright (c) 2025, Resource Factors and contributors
# For license information, please see license.txt

import frappe

def boot_session(bootinfo):
	"""
	Boot session - send whitelabel settings to client
	Called via hooks: boot_session = "rf.api.boot_session"
	"""
	if frappe.session.user != 'Guest':
		try:
			whitelabel_setting = frappe.get_single("Whitelabel Setting")
			bootinfo.whitelabel_setting = whitelabel_setting
		except Exception as e:
			frappe.log_error(f"Error loading Whitelabel Setting: {str(e)}")


def whitelabel_patch():
	"""
	Run whitelabel patches after migrate
	Called via hooks: after_migrate = ['rf.api.whitelabel_patch']
	"""
	try:
		# Delete ERPNext welcome page if it exists
		frappe.delete_doc_if_exists('Page', 'welcome-to-erpnext', force=1)

		# Update Welcome Blog Post content
		if frappe.db.exists("Blog Post", "Welcome"):
			frappe.db.set_value("Blog Post", "Welcome", "content", "")

		# Update onboarding and system settings
		update_onboard_details()
		update_system_settings()

		# Replace ERPNext branding with ERP
		replace_erpnext_branding()

		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Error in whitelabel_patch: {str(e)}")


def update_onboard_details():
	"""Update onboarding settings"""
	try:
		# Check if Whitelabel Setting exists and has hide_onboarding enabled
		if frappe.db.exists("Whitelabel Setting", "Whitelabel Setting"):
			whitelabel_setting = frappe.get_single("Whitelabel Setting")
			if whitelabel_setting.hide_onboarding:
				system_settings = frappe.get_single("System Settings")
				system_settings.setup_complete = 1
				system_settings.save(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(f"Error updating onboard details: {str(e)}")


def update_system_settings():
	"""Update system settings with brand name"""
	try:
		if frappe.db.exists("Whitelabel Setting", "Whitelabel Setting"):
			whitelabel_setting = frappe.get_single("Whitelabel Setting")

			if whitelabel_setting.brand_name:
				system_settings = frappe.get_single("System Settings")
				system_settings.app_name = whitelabel_setting.brand_name
				system_settings.save(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(f"Error updating system settings: {str(e)}")


def replace_erpnext_branding():
	"""
	Replace 'ERPNext' with 'ERP' in workspace titles and other visible areas
	Only updates title field, not the name (ID) to avoid breaking hardcoded references
	"""
	try:
		# Update workspace titles (only title, not name/ID)
		workspaces_to_update = [
			("ERPNext Integrations", "ERP Integrations"),
			("ERPNext Settings", "ERP Settings"),
		]

		for old_title, new_title in workspaces_to_update:
			# Find workspaces with the old title
			workspaces = frappe.get_all(
				"Workspace",
				filters={"title": old_title},
				fields=["name", "title"]
			)

			for workspace in workspaces:
				# Update only the title field, keep the name (ID) unchanged
				frappe.db.set_value("Workspace", workspace.name, "title", new_title, update_modified=False)
				frappe.logger().info(f"Updated workspace title from '{old_title}' to '{new_title}'")

		# Update any Custom HTML blocks or other doctypes that might contain "ERPNext" text
		# This can be extended as needed

	except Exception as e:
		frappe.log_error(f"Error replacing ERPNext branding: {str(e)}")


@frappe.whitelist()
def ignore_update_popup():
	"""
	Override the update popup to prevent showing
	Called via hooks: override_whitelisted_methods
	"""
	return {}
