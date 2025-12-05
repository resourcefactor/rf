# -*- coding: utf-8 -*-
# Copyright (c) 2021, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.installer import update_site_config

class WhitelabelSetting(Document):
	def validate(self):
		system_settings_doc = frappe.get_doc("System Settings","System Settings")
		navbar_settings_doc = frappe.get_doc("Navbar Settings","Navbar Settings")
		website_doc = frappe.get_doc("Website Settings","Website Settings")
		self.set_app_name(system_settings_doc)
		self.set_logo_settings(navbar_settings_doc, website_doc)
		self.disable_onboarding(system_settings_doc)
		self.set_log_notification(system_settings_doc)
		system_settings_doc.save(ignore_permissions = True)
		navbar_settings_doc.save(ignore_permissions = True)
		website_doc.save(ignore_permissions = True)

	def set_app_name(self, system_settings_doc):
		if self.whitelabel_app_name:
			system_settings_doc.app_name = self.whitelabel_app_name
		else:
			if "erpnext" in frappe.get_installed_apps():
				system_settings_doc.app_name = "ERPNext"
			else:
				system_settings_doc.app_name = "Frappe"

	def set_logo_settings(self, navbar_settings_doc, website_doc):
		# Set Navbar Logo - use navbar_logo if set, otherwise use login_page_logo as fallback
		navbar_logo_to_use = self.navbar_logo or self.login_page_logo or ""
		if navbar_logo_to_use:
			# Set in both navbar settings and website settings (navbar may use either)
			navbar_settings_doc.app_logo = navbar_logo_to_use
			website_doc.app_logo = navbar_logo_to_use  # Navbar fallback
			update_site_config("app_logo_url", navbar_logo_to_use)
			frappe.logger().info(f"[Whitelabel] Set navbar logo to: {navbar_logo_to_use}")
		else:
			navbar_settings_doc.app_logo = ""
			website_doc.app_logo = ""
			update_site_config("app_logo_url", False)
			frappe.logger().info("[Whitelabel] Cleared navbar logo")

		# Set Login Page Logo - store in site config for login page override
		if self.login_page_logo:
			# Store login page logo URL in site config for context override
			update_site_config("login_logo_url", self.login_page_logo)
			frappe.logger().info(f"[Whitelabel] Set login logo to: {self.login_page_logo}")
		else:
			update_site_config("login_logo_url", False)
			frappe.logger().info("[Whitelabel] Cleared login logo")

		# Set Splash Page Logo
		if self.splash_page_logo:
			website_doc.splash_image = self.splash_page_logo
			frappe.logger().info(f"[Whitelabel] Set splash logo to: {self.splash_page_logo}")
		else:
			website_doc.splash_image = ""
			frappe.logger().info("[Whitelabel] Cleared splash logo")

		# Set Favicon
		if self.favicon:
			website_doc.favicon = self.favicon
			update_site_config("favicon", self.favicon)
			frappe.logger().info(f"[Whitelabel] Set favicon to: {self.favicon}")
		else:
			website_doc.favicon = ""
			update_site_config("favicon", False)
			frappe.logger().info("[Whitelabel] Cleared favicon")

		frappe.clear_cache()

	def disable_onboarding(self, system_settings_doc):
		if self.ignore_onboard_whitelabel == 1:
			system_settings_doc.enable_onboarding = 0
		else:
			system_settings_doc.enable_onboarding = 1

	def set_log_notification(self, system_settings_doc):
		system_settings_doc.disable_system_update_notification = self.disable_new_update_popup
		system_settings_doc.disable_change_log_notification = self.disable_new_update_popup
