__version__ = "0.0.1"


def _apply_overrides():
	from rf.overrides import accounts_controller, employee_payment_entry, expense_claim

	accounts_controller.apply()
	expense_claim.apply()
	employee_payment_entry.apply()


_apply_overrides()
