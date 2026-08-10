"""Monkey-patch core ERPNext currency validation so it can be toggled off from RF Settings.

`AccountsController.validate_currency` and `GLEntry.validate_currency` are plain instance
methods (not whitelisted methods or doctype classes), so there is no hooks.py entry point
for them. Wrapping them here is the standard way to make a core, non-hookable method
conditionally skippable across every site this app is installed on.
"""

import frappe

import erpnext
from erpnext.accounts.doctype.gl_entry.gl_entry import GLEntry
from erpnext.accounts.party import validate_party_gle_currency
from erpnext.accounts.utils import get_account_currency
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.exceptions import InvalidAccountCurrency

_original_accounts_controller_validate_currency = AccountsController.validate_currency


def bypass_currency_validation():
	return frappe.db.get_single_value("RF Settings", "bypass_currency_validation")


def accounts_controller_validate_currency(self):
	if bypass_currency_validation():
		return
	_original_accounts_controller_validate_currency(self)


def gl_entry_validate_currency(self):
	"""Reimplements GLEntry.validate_currency, keeping the account_currency default
	(other ledger/reconciliation logic depends on it being set correctly) while making
	only the mismatch check itself skippable."""
	if self.is_cancelled:
		return

	company_currency = erpnext.get_company_currency(self.company)
	account_currency = get_account_currency(self.account)

	if not self.account_currency:
		self.account_currency = account_currency or company_currency

	if bypass_currency_validation():
		return

	if account_currency != self.account_currency:
		frappe.throw(
			frappe._("{0} {1}: Accounting Entry for {2} can only be made in currency: {3}").format(
				self.voucher_type, self.voucher_no, self.account, (account_currency or company_currency)
			),
			InvalidAccountCurrency,
		)

	if self.party_type and self.party:
		validate_party_gle_currency(self.party_type, self.party, self.company, self.account_currency)


def apply():
	AccountsController.validate_currency = accounts_controller_validate_currency
	GLEntry.validate_currency = gl_entry_validate_currency
