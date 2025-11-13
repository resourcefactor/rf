import frappe

def execute():
	"""Rename ERPNext Workspaces to ERP Workspaces and remove duplicates"""

	# List of workspaces to rename
	workspace_renames = {
		"ERPNext Integrations": "ERP Integrations",
		"ERPNext Settings": "ERP Settings"
	}

	for old_name, new_name in workspace_renames.items():
		try:
			print(f"\n=== Processing workspace: {old_name} ===")

			# Check if new workspace exists
			new_exists = frappe.db.exists("Workspace", new_name)
			old_exists = frappe.db.exists("Workspace", old_name)

			print(f"Old workspace '{old_name}' exists: {old_exists}")
			print(f"New workspace '{new_name}' exists: {new_exists}")

			if old_exists and not new_exists:
				# Only old exists - rename it
				print(f"Renaming '{old_name}' to '{new_name}'")
				frappe.rename_doc("Workspace", old_name, new_name, force=True, merge=False)
				frappe.db.commit()
				print(f"Successfully renamed workspace")
			elif old_exists and new_exists:
				# Both exist - this is the duplicate issue
				print(f"Both workspaces exist - deleting old workspace '{old_name}'")

				# First, update all references to point to new workspace
				shortcuts = frappe.get_all("Workspace Shortcut",
					filters={"link_to": old_name},
					fields=["name", "parent"])
				for shortcut in shortcuts:
					frappe.db.set_value("Workspace Shortcut", shortcut.name, "link_to", new_name)
					print(f"Updated shortcut in {shortcut.parent}")

				links = frappe.get_all("Workspace Link",
					filters={"link_to": old_name},
					fields=["name", "parent"])
				for link in links:
					frappe.db.set_value("Workspace Link", link.name, "link_to", new_name)
					print(f"Updated link in {link.parent}")

				# Now delete the old workspace
				frappe.delete_doc("Workspace", old_name, force=True, ignore_permissions=True)
				frappe.db.commit()
				print(f"Deleted old workspace '{old_name}'")

			# Ensure the title field is correct on the new/renamed workspace
			if frappe.db.exists("Workspace", new_name):
				doc = frappe.get_doc("Workspace", new_name)
				if doc.title != new_name:
					print(f"Updating title from '{doc.title}' to '{new_name}'")
					doc.title = new_name
					doc.save(ignore_permissions=True)
					frappe.db.commit()

			print(f"=== Finished processing workspace ===\n")

		except Exception as e:
			print(f"ERROR processing workspace {old_name}: {str(e)}")
			import traceback
			traceback.print_exc()
			frappe.log_error(f"Workspace Rename Error: {old_name}", str(e))

	# Clear all caches to remove old workspace references
	print("Clearing all caches...")
	frappe.clear_cache()
	print("Workspace processing completed!")
