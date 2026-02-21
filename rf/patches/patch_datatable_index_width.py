"""
Patch: Fix frappe-datatable index column width for large row counts (1000+)

frappe-datatable uses measureTextWidth() to size the # column, which can
return inaccurate values. This replaces it with a simple digit-based formula:
    digits * 8 + 30  (e.g. 1000 rows = 4 digits → 62px)

Target file:
    node_modules/frappe-datatable/dist/frappe-datatable.cjs.js  (v1.19.0)

After patching, bench build --app frappe is run automatically to recompile
the browser bundles.

Usage:
    bench --site <site> execute rf.patches.patch_datatable_index_width.execute
"""

import os
import subprocess

import frappe


OLD = """    getRowIndexColumnWidth() {
        const rowCount = this.datamanager.getRowCount();
        const padding = 22;
        return $.measureTextWidth(rowCount + '') + padding;
    }"""

NEW = """    getRowIndexColumnWidth() {
        const rowCount = this.datamanager.getRowCount();
        const digits = (rowCount + '').length;
        return digits * 8 + 30;
    }"""


def execute():
	bench_path = frappe.utils.get_bench_path()
	target = os.path.join(
		bench_path,
		"apps", "frappe", "node_modules",
		"frappe-datatable", "dist", "frappe-datatable.cjs.js",
	)

	if not os.path.exists(target):
		print(f"File not found: {target}")
		return

	with open(target, "r") as f:
		content = f.read()

	if NEW.strip() in content:
		print("Already patched — nothing to do.")
		return

	if OLD.strip() not in content:
		print("Pattern not found — frappe-datatable version may have changed.")
		print("Check getRowIndexColumnWidth() in:")
		print(f"  {target}")
		return

	content = content.replace(OLD, NEW)
	with open(target, "w") as f:
		f.write(content)

	print(f"Patched: {target}")

	# Rebuild browser bundles
	print("\nRunning bench build --app frappe ...")
	node_bin = _find_node18(bench_path)
	env = os.environ.copy()
	if node_bin:
		env["PATH"] = os.path.dirname(node_bin) + ":" + env["PATH"]
		print(f"Using node: {node_bin}")

	result = subprocess.run(
		["bench", "build", "--app", "frappe"],
		cwd=bench_path,
		env=env,
	)

	if result.returncode == 0:
		print("\nDone. Hard-refresh your browser (Ctrl+Shift+R) to load the updated bundle.")
	else:
		print("\nbench build failed — you may need to run it manually:")
		print("  source ~/.nvm/nvm.sh && nvm use 18 && bench build --app frappe")


def _find_node18(bench_path):
	"""Try to find a Node >= 18 binary via nvm."""
	nvm_dir = os.path.expanduser("~/.nvm/versions/node")
	if not os.path.isdir(nvm_dir):
		return None

	candidates = []
	for entry in os.listdir(nvm_dir):
		try:
			major = int(entry.lstrip("v").split(".")[0])
			if major >= 18:
				candidates.append((major, os.path.join(nvm_dir, entry, "bin", "node")))
		except ValueError:
			continue

	if not candidates:
		return None

	# Pick highest available version
	candidates.sort(reverse=True)
	node_bin = candidates[0][1]
	return node_bin if os.path.exists(node_bin) else None
