import frappe
from frappe.installer import update_site_config
from frappe.model.document import Document

from rf.whitelabel import apply_whitelabel, save_if_changed


class RFSettings(Document):
	def on_update(self):
		self.push_logos()
		self.push_update_notifications()
		# App name, help rows, footers, CRM rows and onboarding (also re-run after every migrate).
		apply_whitelabel(self)
		frappe.clear_cache()

	def push_logos(self):
		"""Copy logos that are set into the core settings.

		An empty field leaves Website/Navbar Settings alone, so logos configured there directly are
		never wiped. The site_config keys are owned by this app, so they follow the field exactly.
		"""
		website = frappe.get_single("Website Settings")
		navbar = frappe.get_single("Navbar Settings")
		website_values, navbar_values = {}, {}

		if self.navbar_logo:
			navbar_values["app_logo"] = self.navbar_logo
			website_values["app_logo"] = self.navbar_logo
		if self.splash_page_logo:
			website_values["splash_image"] = self.splash_page_logo
		if self.favicon:
			website_values["favicon"] = self.favicon

		save_if_changed(website, website_values)
		save_if_changed(navbar, navbar_values)

		for key, value in (
			("app_logo_url", self.navbar_logo),
			("login_logo_url", self.login_page_logo),
			("favicon", self.favicon),
		):
			if (frappe.conf.get(key) or None) != (value or None):
				# the string "None" removes the key from site_config
				update_site_config(key, value or "None")

	def push_update_notifications(self):
		"""An explicit save follows the checkbox both ways; migrate only ever turns them off."""
		value = 1 if self.disable_new_update_popup else 0
		save_if_changed(
			frappe.get_single("System Settings"),
			{"disable_system_update_notification": value, "disable_change_log_notification": value},
		)
