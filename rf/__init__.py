__version__ = "0.0.1"


def _apply_overrides():
	from rf.overrides import accounts_controller

	accounts_controller.apply()


_apply_overrides()
