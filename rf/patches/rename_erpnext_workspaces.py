import frappe

def execute():
	"""Update ERPNext Workspace titles to ERP (keep document name unchanged)"""

	# List of workspaces to update - only updating title, not document name
	workspace_title_updates = {
		"ERPNext Integrations": "ERP Integrations",
		"ERPNext Settings": "ERP Settings"
	}

	for workspace_name, new_title in workspace_title_updates.items():
		try:
			print(f"\n=== Processing workspace: {workspace_name} ===")

			if frappe.db.exists("Workspace", workspace_name):
				# Get the workspace document
				doc = frappe.get_doc("Workspace", workspace_name)
				current_title = doc.title

				print(f"Workspace '{workspace_name}' found")
				print(f"Current title: '{current_title}'")
				print(f"New title: '{new_title}'")

				# Update the title field only (keep document name as is)
				if current_title != new_title:
					doc.title = new_title
					doc.save(ignore_permissions=True)
					frappe.db.commit()
					print(f"✓ Updated title successfully")
				else:
					print(f"✓ Title already correct")

				print(f"Document name remains: '{workspace_name}'")
			else:
				print(f"Workspace '{workspace_name}' not found, skipping")

			print(f"=== Finished processing workspace ===\n")

		except Exception as e:
			print(f"ERROR processing workspace {workspace_name}: {str(e)}")
			import traceback
			traceback.print_exc()
			frappe.log_error(f"Workspace Title Update Error: {workspace_name}", str(e))

	# Clear all caches to reflect title changes
	print("Clearing all caches...")
	frappe.clear_cache()
	print("Workspace title updates completed!")
