frappe.ui.form.on('Task', {
	refresh: function (frm) {
		if (!frm.is_new()) {
			if (frm.doc.github_pr) {
				frm.add_custom_button(__("Pull Request"), () => {
					window.open(frm.doc.github_pr);
				}, __("Go to"));
			};
		}
	},
	github_pr: function (frm) {
		frm.set_value('status', 'Needs Code Review')
	}
});