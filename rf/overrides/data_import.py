"""Optionally lift Frappe's Data Import restrictions on which DocTypes can be imported.

`DataImport.validate_doctype()` (frappe/core/doctype/data_import/data_import.py) refuses core
DocTypes such as Property Setter (a hardcoded blocklist) and any DocType that does not have
"Allow Import" ticked. When "Allow Import for All DocTypes" is checked in Whitelabel Setting, both of those
checks are skipped. The user still needs the "import" permission on the DocType, so this does not
bypass role permissions.
"""

import frappe
from frappe import _
from frappe.core.doctype.data_import.data_import import DataImport

_original_validate_doctype = DataImport.validate_doctype


def allow_import_for_all_doctypes():
	try:
		return frappe.db.get_single_value("Whitelabel Setting", "allow_import_for_all_doctypes")
	except Exception:
		# Whitelabel Setting is not installed / migrated yet
		return False


def validate_doctype(self):
	if not allow_import_for_all_doctypes():
		return _original_validate_doctype(self)

	if not frappe.has_permission(self.reference_doctype, "import"):
		frappe.throw(
			_("You do not have import permission for {0}").format(self.reference_doctype),
			frappe.PermissionError,
		)


def apply():
	DataImport.validate_doctype = validate_doctype
