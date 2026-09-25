frappe.ui.form.on("Company", {
	refresh(frm) {
		if (!frappe.boot.rf_can_delete_company_transactions) {
			frm.remove_custom_button(__("Delete Transactions"), __("Manage"));
		}
	},
});
