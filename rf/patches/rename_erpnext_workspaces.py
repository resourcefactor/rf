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
					frappe.rename_doc("Workspace", old_name, new_name, force=True, merge=False)
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

			# Update workspace shortcuts pointing to old workspace
			shortcuts = frappe.get_all("Workspace Shortcut",
				filters={"link_to": old_name},
				fields=["name", "parent"])
			for shortcut in shortcuts:
				frappe.db.set_value("Workspace Shortcut", shortcut.name, "link_to", new_name)
				print(f"Updated shortcut in {shortcut.parent}")

			# Update workspace links pointing to old workspace
			links = frappe.get_all("Workspace Link",
				filters={"link_to": old_name},
				fields=["name", "parent"])
			for link in links:
				frappe.db.set_value("Workspace Link", link.name, "link_to", new_name)
				print(f"Updated link in {link.parent}")

			frappe.db.commit()

			# Clear all caches to remove old workspace references
			frappe.clear_cache()

			if not frappe.db.exists("Workspace", old_name) and frappe.db.exists("Workspace", new_name):
				print(f"Successfully renamed and configured: {old_name} -> {new_name}")
			else:
				print(f"Workspace {old_name} not found, skipping")

		except Exception as e:
			print(f"Error renaming workspace {old_name}: {str(e)}")
			frappe.log_error(f"Workspace Rename Error: {old_name}", str(e))
