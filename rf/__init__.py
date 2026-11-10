__version__ = "0.0.1"


def _apply_overrides():
	from rf.overrides import data_import

	data_import.apply()


_apply_overrides()
