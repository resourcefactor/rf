import frappe
from frappe.installer import update_site_config
from frappe.model.document import Document


class RFSettings(Document):
	def validate(self):
		system_settings_doc = frappe.get_doc("System Settings", "System Settings")
		navbar_settings_doc = frappe.get_doc("Navbar Settings", "Navbar Settings")
		website_doc = frappe.get_doc("Website Settings", "Website Settings")
		self.set_app_name(system_settings_doc)
		self.set_logo_settings(navbar_settings_doc, website_doc)
		self.set_log_notification(system_settings_doc)
		system_settings_doc.save(ignore_permissions=True)
		navbar_settings_doc.save(ignore_permissions=True)
		website_doc.save(ignore_permissions=True)

	def set_app_name(self, system_settings_doc):
		if self.whitelabel_app_name:
			system_settings_doc.app_name = self.whitelabel_app_name
		else:
			if "erpnext" in frappe.get_installed_apps():
				system_settings_doc.app_name = "ERPNext"
			else:
				system_settings_doc.app_name = "Frappe"

	def set_logo_settings(self, navbar_settings_doc, website_doc):
		if self.navbar_logo:
			navbar_settings_doc.app_logo = self.navbar_logo
			website_doc.app_logo = self.navbar_logo
			update_site_config("app_logo_url", self.navbar_logo)
		else:
			navbar_settings_doc.app_logo = ""
			website_doc.app_logo = ""
			update_site_config("app_logo_url", False)

		if self.login_page_logo:
			update_site_config("login_logo_url", self.login_page_logo)
		else:
			update_site_config("login_logo_url", False)

		if self.splash_page_logo:
			website_doc.splash_image = self.splash_page_logo
		else:
			website_doc.splash_image = ""

		if self.favicon:
			website_doc.favicon = self.favicon
			update_site_config("favicon", self.favicon)
		else:
			website_doc.favicon = ""
			update_site_config("favicon", False)

		frappe.clear_cache()

	def set_log_notification(self, system_settings_doc):
		system_settings_doc.disable_system_update_notification = self.disable_new_update_popup
		system_settings_doc.disable_change_log_notification = self.disable_new_update_popup
