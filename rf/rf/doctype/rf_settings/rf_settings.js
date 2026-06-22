frappe.ui.form.on('RF Settings', {
	after_save(frm) {
		frappe.ui.toolbar.clear_cache();
	},
});
