"""Fix Expense Claim GL entries for foreign-currency claims paid against company-currency accounts.

`ExpenseClaim.get_gl_entries()` (hrms/hr/doctype/expense_claim/expense_claim.py) hardcodes
`account_currency=self.currency` on every GL line, and fills `debit_in_account_currency` /
`credit_in_account_currency` with the claim's own foreign-currency amounts (e.g. grand_total)
regardless of what currency the target account (payable/expense/payment) is actually held in.

For the common case where those accounts are in company currency, this posts GL Entries whose
`account_currency` doesn't match the account's real currency, and whose "in account currency"
amounts are the *foreign* total instead of the converted base total (e.g. CNY 2000 stored
against an AED account instead of AED 119.90). Downstream currency validation is the only
thing that catches this; without it, the wrong amount silently flows into the ledger and any
Payment Entry reference built from it.

This patch corrects those GL lines after the fact: for any line whose account is genuinely
held in company currency, it re-points account_currency there and uses the already-correct
base_ amount as the account-currency amount too.
"""

import frappe
from frappe.utils import cstr, flt

import erpnext
from erpnext.accounts.utils import get_account_currency
from hrms.hr.doctype.expense_claim.expense_claim import ExpenseClaim

_original_get_gl_entries = ExpenseClaim.get_gl_entries


def expense_claim_get_gl_entries(self):
	gl_entries = _original_get_gl_entries(self)

	if self.currency == self.company_currency:
		return gl_entries

	company_currency = erpnext.get_company_currency(self.company)

	for entry in gl_entries:
		if not entry.get("account"):
			continue

		real_account_currency = get_account_currency(entry["account"])

		# Only correct the common case: the account is genuinely in company currency but
		# was mislabeled as the claim's currency. A true third-currency account would need
		# its own exchange rate, which this claim doesn't carry, so leave that case alone.
		if real_account_currency != company_currency or real_account_currency == self.currency:
			continue

		entry["account_currency"] = real_account_currency
		if entry.get("debit"):
			entry["debit_in_account_currency"] = entry["debit"]
		if entry.get("credit"):
			entry["credit_in_account_currency"] = entry["credit"]

	return gl_entries


def expense_claim_set_status(self, update=False):
	"""ExpenseClaim.set_status() compares grand_total (claim's own currency) against
	total_amount_reimbursed, which is accumulated in the *payable account's* currency
	(see get_total_reimbursed_amount). For a foreign-currency claim reimbursed through a
	company-currency account those can never match, so the claim stays "Unpaid" forever
	even once fully settled. Compare against base_grand_total instead in that case."""
	status = {"0": "Draft", "1": "Submitted", "2": "Cancelled"}[cstr(self.docstatus or 0)]

	if self.currency != self.company_currency:
		reimbursable_total = self.base_grand_total
		precision = self.precision("base_grand_total")
	else:
		reimbursable_total = self.grand_total
		precision = self.precision("grand_total")

	if self.docstatus == 1:
		if self.approval_status == "Approved":
			if (
				self.is_paid
				or (
					flt(self.total_sanctioned_amount) > 0
					and (
						(flt(reimbursable_total, precision) == flt(self.total_amount_reimbursed, precision))
						or (flt(reimbursable_total, precision) == 0)
					)
				)
			):
				status = "Paid"
			elif flt(self.total_sanctioned_amount) > 0:
				status = "Unpaid"
		elif self.approval_status == "Rejected":
			status = "Rejected"

	if update:
		self.db_set("status", status)
		self.publish_update()
		self.notify_update()
	else:
		self.status = status


def apply():
	ExpenseClaim.get_gl_entries = expense_claim_get_gl_entries
	ExpenseClaim.set_status = expense_claim_set_status
