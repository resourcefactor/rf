app_name = "rf"
app_title = "Rf"
app_publisher = "Resource Factors"
app_description = "RF"
app_email = "it@resourcefactors.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "rf",
# 		"logo": "/assets/rf/logo.png",
# 		"title": "Rf",
# 		"route": "/rf",
# 		"has_permission": "rf.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/rf/css/whitelabel_app.css"
app_include_js = "whitelabel.bundle.js"

# include js, css files in header of web template
web_include_css = "/assets/rf/css/whitelabel_web.css"
# web_include_js = "/assets/rf/js/rf.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "rf/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "rf/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website Context
# ---------------
website_context = {
	"favicon": "/assets/rf/images/whitelabel_logo.svg",
	"splash_image": "/assets/rf/images/whitelabel_logo.svg"
}

# Update website context dynamically for login page
update_website_context = "rf.api.get_website_context"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "rf.utils.jinja_methods",
# 	"filters": "rf.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "rf.install.before_install"
# after_install = "rf.install.after_install"

# After Migrate
# -------------
after_migrate = ['rf.api.whitelabel_patch']

# Boot Session
# ------------
boot_session = "rf.api.boot_session"

# Uninstallation
# ------------

# before_uninstall = "rf.uninstall.before_uninstall"
# after_uninstall = "rf.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "rf.utils.before_app_install"
# after_app_install = "rf.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "rf.utils.before_app_uninstall"
# after_app_uninstall = "rf.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rf.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"rf.tasks.all"
# 	],
# 	"daily": [
# 		"rf.tasks.daily"
# 	],
# 	"hourly": [
# 		"rf.tasks.hourly"
# 	],
# 	"weekly": [
# 		"rf.tasks.weekly"
# 	],
# 	"monthly": [
# 		"rf.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "rf.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.utils.change_log.show_update_popup": "rf.api.ignore_update_popup"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "rf.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["rf.utils.before_request"]
# after_request = ["rf.utils.after_request"]

# Job Events
# ----------
# before_job = ["rf.utils.before_job"]
# after_job = ["rf.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"rf.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Fixtures
# --------
fixtures = [
    {"dt": "Custom Field", "filters": [["Translation","source_text","like","%ERPNext%"]]}
]

# Brand Settings
# --------------
brand_html = (
    '<div><img  src="/assets/rf/images/whitelabel_logo_long.svg"> </div>'
)

brand_name = "Resource Factors"
