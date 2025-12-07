import frappe
from frappe import _

def get_context(context):
	"""Custom login page context"""
	# Get login logo from site config
	login_logo_url = frappe.conf.get("login_logo_url")
	app_logo_url = frappe.conf.get("app_logo_url")

	# Pass logos to template context
	if login_logo_url:
		context["login_logo_url"] = login_logo_url
		frappe.logger().debug(f"[Whitelabel] Custom login page using logo: {login_logo_url}")

	if app_logo_url:
		context["app_logo_url"] = app_logo_url

	# Allow Frappe's default login page behavior
	context.no_cache = 1

	return context
