# Copyright (c) 2025, Resource Factors and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WhitelabelSetting(Document):
	def validate(self):
		"""Apply whitelabel settings to system"""
		self.update_system_settings()
		self.update_navbar_settings()

	def update_system_settings(self):
		"""Update System Settings with whitelabel preferences"""
		try:
			system_settings = frappe.get_single("System Settings")

			# Hide onboarding if configured
			if self.hide_onboarding:
				system_settings.setup_complete = 1

			# Set app name if provided
			if self.whitelabel_app_name:
				system_settings.app_name = self.whitelabel_app_name

			system_settings.save(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error updating System Settings: {str(e)}")

	def update_navbar_settings(self):
		"""Update Navbar Settings to hide help menu items if needed"""
		try:
			if not self.show_help_menu:
				navbar_settings = frappe.get_single("Navbar Settings")

				# Hide all help dropdown items
				for item in navbar_settings.help_dropdown:
					if not item.hidden:
						item.hidden = 1

				navbar_settings.save(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error updating Navbar Settings: {str(e)}")
