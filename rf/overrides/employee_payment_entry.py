"""Fix Payment Entry reference amounts for Expense Claims paid against company-currency accounts.

`hrms.overrides.employee_payment_entry.get_total_amount_and_exchange_rate()` (used when
populating Payment Entry "references" for Employee-party payments, e.g. via "Get Outstanding
Invoices") reads `total_sanctioned_amount` / `total_taxes_and_charges` unconditionally, which
are in the *claim's own currency*. It never checks `party_account_currency`, so a foreign
currency claim (e.g. CNY) reimbursed through a company-currency account (e.g. AED) shows the
raw foreign total as if it were the payable-account amount (CNY 2000 displayed as AED 2000
instead of the converted AED 119.90).

This mirrors the bug fixed in expense_claim.py's get_gl_entries: the fix is to use the base_
(company currency) amounts whenever the account being paid is genuinely in company currency,
same as ERPNext's own erpnext.accounts.doctype.payment_entry.payment_entry.get_reference_details
already does for non-employee doctypes.
"""

import frappe
from frappe.utils import flt

import erpnext
from hrms.overrides import employee_payment_entry as hrms_epe

_original_get_reference_details_for_employee = hrms_epe.get_reference_details_for_employee
_original_get_grand_total_and_outstanding_amount = hrms_epe.get_grand_total_and_outstanding_amount


def get_reference_details_for_employee(
	reference_doctype: str, reference_name: str, party_account_currency: str
):
	if reference_doctype != "Expense Claim":
		return _original_get_reference_details_for_employee(
			reference_doctype, reference_name, party_account_currency
		)

	frappe.has_permission(reference_doctype, "read", reference_name, throw=True)
	ref_doc = frappe.get_doc(reference_doctype, reference_name)
	company_currency = ref_doc.get("company_currency") or erpnext.get_company_currency(ref_doc.company)

	# Only correct the common case: a foreign-currency claim reimbursed through an account
	# genuinely held in company currency. Same-currency claims are already handled correctly
	# by the original function.
	if not (party_account_currency == company_currency and party_account_currency != ref_doc.currency):
		return _original_get_reference_details_for_employee(
			reference_doctype, reference_name, party_account_currency
		)

	total_amount = flt(ref_doc.base_total_sanctioned_amount) + flt(ref_doc.base_total_taxes_and_charges)
	# total_amount_reimbursed is summed from GL/Payment Ledger amounts already posted in the
	# payable account's currency (see get_total_reimbursed_amount), so it needs no conversion.
	outstanding_amount = (
		total_amount - flt(ref_doc.total_amount_reimbursed) - flt(ref_doc.base_total_advance_amount)
	)

	precision = frappe.get_precision("Expense Claim", "grand_total")
	return frappe._dict(
		{
			"due_date": ref_doc.get("due_date"),
			"total_amount": flt(total_amount),
			"outstanding_amount": flt(outstanding_amount, precision),
			"exchange_rate": 1,
		}
	)


def get_grand_total_and_outstanding_amount(doc, party_amount, party_account_currency):
	"""Same bug, same fix, different entry point: this backs the "Create > Payment" button
	on the Expense Claim form itself, separate from the Payment Entry "Get Outstanding
	Invoices" path fixed by get_reference_details_for_employee above."""
	if not (
		doc.doctype == "Expense Claim"
		and not party_amount
		and party_account_currency == doc.company_currency
		and party_account_currency != doc.currency
	):
		return _original_get_grand_total_and_outstanding_amount(doc, party_amount, party_account_currency)

	grand_total = flt(doc.base_total_sanctioned_amount) + flt(doc.base_total_taxes_and_charges)
	outstanding_amount = (
		grand_total - flt(doc.total_amount_reimbursed) - flt(doc.base_total_advance_amount)
	)
	return grand_total, outstanding_amount


def apply():
	hrms_epe.get_reference_details_for_employee = get_reference_details_for_employee
	hrms_epe.get_grand_total_and_outstanding_amount = get_grand_total_and_outstanding_amount
