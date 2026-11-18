from unittest.mock import call, patch

import frappe
from frappe.tests import IntegrationTestCase

import rf.environment
from rf.environment import DEFAULT_COLORS, get_environment, get_text_color

# The only link is User (Users Allowed to Delete Transactions), which these tests don't use. Without
# this, building User test records pulls in ERPNext's bootstrap data, which fails on demo sites.
IGNORE_TEST_RECORD_DEPENDENCIES = ["User"]


def site_config(environment=None, label=None, color=None):
	"""Stand-in site_config values for the environment keys (None reads as unset)."""
	return patch(
		"rf.environment.read_config",
		return_value={
			"rf_environment": environment,
			"rf_environment_label": label,
			"rf_environment_color": color,
		},
	)


class TestEnvironment(IntegrationTestCase):
	def test_no_environment_draws_no_bar(self):
		with site_config():
			self.assertIsNone(get_environment())
		with site_config(environment="  "):
			self.assertIsNone(get_environment())

	def test_production_is_the_default_and_has_no_bar(self):
		self.assertNotIn("Production", frappe.get_meta("RF Settings").get_options("environment").split("\n"))
		# an explicit value, e.g. from `bench set-config rf_environment Production`, reads as unset
		for value in ("Production", " production "):
			with patch("frappe.get_site_config", return_value=frappe._dict(rf_environment=value)):
				self.assertIsNone(rf.environment.read_config()["rf_environment"])
				self.assertIsNone(get_environment())

	def test_defaults_per_environment(self):
		for environment, color in DEFAULT_COLORS.items():
			with site_config(environment=environment):
				env = get_environment()
			self.assertEqual(env["environment"], environment)
			self.assertEqual(env["label"], environment.upper())
			self.assertEqual(env["color"], color)

	def test_custom_label_and_color(self):
		with site_config(environment="Staging", label="Training copy", color="#0f0"):
			env = get_environment()
		self.assertEqual(env["label"], "Training copy")
		self.assertEqual(env["color"], "#0f0")

	def test_invalid_color_falls_back_to_default(self):
		# e.g. a hand-edited site_config; it must never reach the page as CSS
		with site_config(environment="UAT", color="red; display:none"):
			self.assertEqual(get_environment()["color"], DEFAULT_COLORS["UAT"])
		with site_config(environment="Something Else"):
			self.assertEqual(get_environment()["color"], "#6B7280")

	def test_text_color_contrast(self):
		self.assertEqual(get_text_color("#F59E0B"), "#111827")  # amber: dark text
		self.assertEqual(get_text_color("#FFFFFF"), "#111827")
		self.assertEqual(get_text_color("#fff"), "#111827")
		for dark in ("#DC2626", "#7C3AED", "#2563EB", "#000"):
			self.assertEqual(get_text_color(dark), "#FFFFFF", dark)


class TestRFSettingsEnvironment(IntegrationTestCase):
	def test_fields_come_from_site_config_not_the_database(self):
		# another site's backup restored onto this one carries that site's values in tabSingles
		frappe.db.set_single_value(
			"RF Settings",
			{"environment": "Development", "environment_label": "DEV", "environment_color": "#2563EB"},
		)
		with site_config(environment="Staging"):
			doc = frappe.get_doc("RF Settings")
		self.assertEqual(doc.environment, "Staging")
		self.assertIsNone(doc.environment_label)
		self.assertIsNone(doc.environment_color)

		with site_config():
			self.assertIsNone(frappe.get_doc("RF Settings").environment)

	def test_clearing_environment_clears_text_and_color(self):
		with site_config(environment="Staging", label="Training", color="#123456"):
			doc = frappe.get_doc("RF Settings")
		doc.environment = ""
		doc.run_method("validate")
		self.assertIsNone(doc.environment_label)
		self.assertIsNone(doc.environment_color)

	def test_push_writes_only_changed_keys(self):
		path = "rf.rf.doctype.rf_settings.rf_settings.update_site_config"
		with site_config(environment="Staging", color="#123456"):
			doc = frappe.get_doc("RF Settings")
			doc.environment = "UAT"
			doc.environment_label = "  "  # blank stays unset
			doc.environment_color = ""  # cleared
			with patch(path) as update_site_config:
				doc.push_environment()
		self.assertEqual(
			update_site_config.call_args_list,
			[call("rf_environment", "UAT"), call("rf_environment_color", "None")],
		)

		with site_config(environment="Staging"):
			doc = frappe.get_doc("RF Settings")
			with patch(path) as update_site_config:
				doc.push_environment()
		update_site_config.assert_not_called()
