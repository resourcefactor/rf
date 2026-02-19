"""
Patch: Fix frappe-datatable index column width for large row counts (1000+)

The _rowIndex column in frappe-datatable uses measureTextWidth() to calculate
its width, but this can return inaccurate values. This patch adds a minimum
width based on digit count so the column is never too narrow.

Usage:
    bench --site pos execute rf.patches.patch_datatable_index_width.execute
"""

import os
import re
import frappe


def execute():
	bench_path = frappe.utils.get_bench_path()
	datatable_path = os.path.join(bench_path, "apps", "frappe", "node_modules", "frappe-datatable")

	files_patched = 0

	# 1. Patch dist/frappe-datatable.js
	dist_file = os.path.join(datatable_path, "dist", "frappe-datatable.js")
	if os.path.exists(dist_file):
		files_patched += _patch_dist(dist_file)

	# 2. Patch dist/frappe-datatable.min.js
	min_file = os.path.join(datatable_path, "dist", "frappe-datatable.min.js")
	if os.path.exists(min_file):
		files_patched += _patch_min(min_file)

	# 3. Patch src/style.js
	src_file = os.path.join(datatable_path, "src", "style.js")
	if os.path.exists(src_file):
		files_patched += _patch_dist(src_file)

	if files_patched:
		print(f"Datatable index width patch applied to {files_patched} file(s).")
	else:
		print("Patch already applied or files not found.")


def _patch_dist(filepath):
	"""Patch the readable JS files (dist and src)."""
	with open(filepath, "r") as f:
		content = f.read()

	old = (
		"getRowIndexColumnWidth() {\n"
		"            const rowCount = this.datamanager.getRowCount();\n"
		"            const padding = 22;\n"
		"            return $.measureTextWidth(rowCount + '') + padding;\n"
		"        }"
	)

	# Handle src/style.js with different indentation
	old_src = (
		"getRowIndexColumnWidth() {\n"
		"        const rowCount = this.datamanager.getRowCount();\n"
		"        const padding = 22;\n"
		"        return $.measureTextWidth(rowCount + '') + padding;\n"
		"    }"
	)

	new_template = (
		"getRowIndexColumnWidth() {{\n"
		"{indent}const rowCount = this.datamanager.getRowCount();\n"
		"{indent}const padding = 22;\n"
		"{indent}const digits = (rowCount + '').length;\n"
		"{indent}const minWidth = digits * 10 + padding;\n"
		"{indent}const measuredWidth = $.measureTextWidth(rowCount + '') + padding;\n"
		"{indent}return Math.max(measuredWidth, minWidth);\n"
		"{close_indent}}}"
	)

	if old in content:
		new_code = new_template.format(indent="            ", close_indent="        ")
		content = content.replace(old, new_code)
	elif old_src in content:
		new_code = new_template.format(indent="        ", close_indent="    ")
		content = content.replace(old_src, new_code)
	else:
		# Already patched or different version
		if "minWidth" in content and "getRowIndexColumnWidth" in content:
			print(f"  Already patched: {filepath}")
			return 0
		print(f"  Could not match pattern in: {filepath}")
		return 0

	with open(filepath, "w") as f:
		f.write(content)

	print(f"  Patched: {filepath}")
	return 1


def _patch_min(filepath):
	"""Patch the minified JS file."""
	with open(filepath, "r") as f:
		content = f.read()

	old_min = "getRowIndexColumnWidth(){const t=this.datamanager.getRowCount();return e.measureTextWidth(t+\"\")+22}"
	new_min = (
		"getRowIndexColumnWidth(){"
		"const t=this.datamanager.getRowCount(),n=22,i=(t+\"\").length,o=i*10+n,"
		"s=e.measureTextWidth(t+\"\")+n;return Math.max(s,o)}"
	)

	if old_min in content:
		content = content.replace(old_min, new_min)
	else:
		if "minWidth" in content or ("Math.max" in content and "getRowIndexColumnWidth" in content):
			print(f"  Already patched: {filepath}")
			return 0
		print(f"  Could not match pattern in: {filepath}")
		return 0

	with open(filepath, "w") as f:
		f.write(content)

	print(f"  Patched: {filepath}")
	return 1
