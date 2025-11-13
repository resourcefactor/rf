import frappe

def execute():
	"""Rename ERPNext Workspaces to ERP Workspaces"""

	# List of workspaces to rename
	workspace_renames = {
		"ERPNext Integrations": "ERP Integrations",
		"ERPNext Settings": "ERP Settings"
	}

	for old_name, new_name in workspace_renames.items():
		try:
			# Check if old workspace exists
			if frappe.db.exists("Workspace", old_name):
				# Check if new workspace already exists
				if not frappe.db.exists("Workspace", new_name):
					# Rename the workspace
					frappe.rename_doc("Workspace", old_name, new_name, force=True)
					frappe.db.commit()
					print(f"Renamed workspace: {old_name} -> {new_name}")
				else:
					print(f"Workspace {new_name} already exists, skipping rename")

			# Update the title field regardless (in case workspace exists with old title)
			if frappe.db.exists("Workspace", new_name):
				doc = frappe.get_doc("Workspace", new_name)
				if doc.title != new_name:
					doc.title = new_name
					doc.save(ignore_permissions=True)
					frappe.db.commit()
					print(f"Updated workspace title: {new_name}")
			else:
				print(f"Workspace {old_name} not found, skipping")
		except Exception as e:
			print(f"Error renaming workspace {old_name}: {str(e)}")
			frappe.log_error(f"Workspace Rename Error: {old_name}", str(e))
