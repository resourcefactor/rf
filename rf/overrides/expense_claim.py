"""Fix Expense Claim GL entries and outstanding-amount calculations for foreign-currency claims
paid against company-currency accounts.

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

`get_outstanding_amount_for_claim()` has a parallel bug: it computes
    total_sanctioned_amount (foreign) - total_amount_reimbursed (company currency) - ...
which mixes currencies and produces a nonsense outstanding (e.g. CNY 10,000 - AED 599.50 =
9,400.50 AED stored back into the Payment Entry Reference row). This patch replaces that
function with one that uses base_ (company-currency) amounts for foreign-currency claims,
matching what update_outstanding_amount_in_payment_entry then writes to the PE Reference.
"""

import frappe
from frappe.utils import cstr, flt

import erpnext
import hrms.hr.doctype.expense_claim.expense_claim as hrms_expense_claim
from erpnext.accounts.utils import get_account_currency
from hrms.hr.doctype.expense_claim.expense_claim import ExpenseClaim

_original_get_gl_entries = ExpenseClaim.get_gl_entries
_original_get_outstanding_amount_for_claim = hrms_expense_claim.get_outstanding_amount_for_claim


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


def get_outstanding_amount_for_claim(claim):
	"""Patched version that uses base (company-currency) amounts for foreign-currency claims.

	The original computes:
	    total_sanctioned_amount (claim currency) - total_amount_reimbursed (payable account currency)
	For foreign-currency claims reimbursed through a company-currency account, those two values
	are in different currencies, so the subtraction produces a nonsense result (e.g.
	CNY 10,000 - AED 599.50 = 9,400.50) that then gets written back into the Payment Entry
	Reference outstanding_amount field by update_outstanding_amount_in_payment_entry().

	For same-currency claims the original logic is unchanged.
	"""
	precision = frappe.get_precision("Expense Claim", "grand_total")

	if isinstance(claim, str):
		claim = frappe.db.get_value(
			"Expense Claim",
			claim,
			(
				"total_sanctioned_amount",
				"total_taxes_and_charges",
				"total_amount_reimbursed",
				"total_advance_amount",
				"base_total_sanctioned_amount",
				"base_total_taxes_and_charges",
				"base_total_advance_amount",
				"currency",
				"company",
			),
			as_dict=True,
		)

	company_currency = erpnext.get_company_currency(claim.company)

	if claim.currency != company_currency:
		# total_amount_reimbursed is accumulated from GL/Payment Ledger entries already
		# posted in the payable account's currency (company currency), so it needs no
		# conversion — only the sanctioned/advance amounts must be switched to base_.
		outstanding_amt = (
			flt(claim.base_total_sanctioned_amount)
			+ flt(claim.base_total_taxes_and_charges)
			- flt(claim.total_amount_reimbursed)
			- flt(claim.base_total_advance_amount)
		)
	else:
		outstanding_amt = (
			flt(claim.total_sanctioned_amount)
			+ flt(claim.total_taxes_and_charges)
			- flt(claim.total_amount_reimbursed)
			- flt(claim.total_advance_amount)
		)

	return flt(outstanding_amt, precision)


def apply():
	ExpenseClaim.get_gl_entries = expense_claim_get_gl_entries
	ExpenseClaim.set_status = expense_claim_set_status
	# Patch the module-level function so update_outstanding_amount_in_payment_entry (and any
	# other caller that imports from the module) picks up the fixed version.
	hrms_expense_claim.get_outstanding_amount_for_claim = get_outstanding_amount_for_claim
	# Also re-bind the name in hrms.overrides.employee_payment_entry, which imported the
	# function by name at module load time and therefore holds a stale reference.
	import hrms.overrides.employee_payment_entry as hrms_epe

	hrms_epe.get_outstanding_amount_for_claim = get_outstanding_amount_for_claim
