"""Monkey-patch core ERPNext currency validation so it can be toggled off from RF Settings.

`AccountsController.validate_currency` and `GLEntry.validate_currency` are plain instance
methods (not whitelisted methods or doctype classes), so there is no hooks.py entry point
for them. Wrapping them here is the standard way to make a core, non-hookable method
conditionally skippable across every site this app is installed on.
"""

import frappe
from erpnext.accounts.doctype.gl_entry.gl_entry import GLEntry
from erpnext.controllers.accounts_controller import AccountsController

_original_accounts_controller_validate_currency = AccountsController.validate_currency
_original_gl_entry_validate_currency = GLEntry.validate_currency


def bypass_currency_validation():
	return frappe.db.get_single_value("RF Settings", "bypass_currency_validation")


def accounts_controller_validate_currency(self):
	if bypass_currency_validation():
		return
	_original_accounts_controller_validate_currency(self)


def gl_entry_validate_currency(self):
	if bypass_currency_validation():
		return
	_original_gl_entry_validate_currency(self)


def apply():
	AccountsController.validate_currency = accounts_controller_validate_currency
	GLEntry.validate_currency = gl_entry_validate_currency
