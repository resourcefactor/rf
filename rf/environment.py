"""Per-site environment marker (Staging / UAT / Development) shown as a coloured bar across the desk.

No environment means production, which keeps the normal desk with no bar.

The values live in the site's own site_config.json, not in the database, so they stay with the site:
a staging site restored from a production backup still says Staging. RF Settings is the UI for them --
its fields are read from site_config on load and written back on save (see RFSettings). They can also
be set from the shell with `bench --site <site> set-config rf_environment Staging`.

The keys are read from disk (`read_config`), not from `frappe.conf`: that is cached per worker for 60s
with no cross-worker invalidation, so after a save the next page load could hit a worker that still
has the old value. The file is tiny and read once per desk load.
"""

import re

import frappe
from frappe import _

# RF Settings field -> site_config key
SITE_CONFIG_KEYS = {
	"environment": "rf_environment",
	"environment_label": "rf_environment_label",
	"environment_color": "rf_environment_color",
}

DEFAULT_COLORS = {
	"Staging": "#F59E0B",
	"UAT": "#7C3AED",
	"Development": "#2563EB",
}
FALLBACK_COLOR = "#6B7280"
HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


def read_config():
	"""This site's environment keys, fresh from site_config.json (and common_site_config.json)."""
	config = frappe.get_site_config()
	values = {key: config.get(key) for key in SITE_CONFIG_KEYS.values()}
	# Production is the default, not an option: an explicit "Production" (e.g. from set-config) reads
	# as unset, so it draws no bar and doesn't fail the Select's options check on the next save.
	if (values["rf_environment"] or "").strip().lower() == "production":
		values["rf_environment"] = None
	return values


def get_environment():
	"""The bar to draw on this site, or None when no environment is set."""
	config = read_config()
	environment = (config.get("rf_environment") or "").strip()
	if not environment:
		return None

	color = (config.get("rf_environment_color") or "").strip()
	if not HEX_COLOR.match(color):
		# empty, or a hand-edited value that isn't a hex colour
		color = DEFAULT_COLORS.get(environment, FALLBACK_COLOR)

	return {
		"environment": environment,
		"label": (config.get("rf_environment_label") or "").strip() or _(environment).upper(),
		"color": color,
		"text_color": get_text_color(color),
	}


def get_text_color(hex_color):
	"""Black or white, whichever has more contrast with the bar colour (WCAG relative luminance)."""
	digits = hex_color.lstrip("#")
	if len(digits) == 3:
		digits = "".join(c * 2 for c in digits)

	def channel(pair):
		c = int(pair, 16) / 255
		return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

	r, g, b = (channel(digits[i : i + 2]) for i in (0, 2, 4))
	luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
	# Contrast with white and with black are equal at a luminance of about 0.179.
	return "#111827" if luminance > 0.179 else "#FFFFFF"
