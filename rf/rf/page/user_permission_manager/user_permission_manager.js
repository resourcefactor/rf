frappe.pages['user-permission-manager'].on_page_load = function(wrapper) {
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('User Permission Manager'),
		single_column: true,
	});
	new UserPermissionManager(page);
};

function UserPermissionManager(page) {
	this.page = page;
	this.original_checked = [];
	this.values_filter = '';
	this.debounce_timer = null;
	// Bumped on every scope change (user/allow/applicable_for/apply_to_all).
	// Async callbacks compare their captured token against the current one
	// before applying results, so a slow/out-of-order response from a
	// superseded scope can never overwrite newer state (or a newer
	// in-progress checkbox click) once the user has moved on.
	this.scope_token = 0;
	// One-shot flag: only the Values-filter path sets this before refreshing,
	// so a same-scope refetch preserves in-flight checkbox clicks. See
	// fetch_grid_options().
	this.preserve_checked_on_next_fetch = false;

	// Wrappers are created in visual (top-to-bottom) order first, then filled in.
	// The grid control object must exist before make_filter_controls() runs, since
	// several filter onchange handlers call this.grid_control.refresh() as a side
	// effect of setting their initial value.
	this.filter_area = $('<div class="upm-filters" style="margin-bottom: 15px;"></div>').appendTo(this.page.main);
	this.cap_note = $(`<div class="text-muted small upm-cap-note" style="display:none; margin-bottom: 10px;">
		${__('Showing first 100 matches — refine Values filter to narrow further')}
	</div>`).appendTo(this.page.main);
	this.grid_wrapper = $('<div class="upm-grid"></div>').appendTo(this.page.main);

	this.make_grid_control();
	this.make_filter_controls();
	this.make_save_button();
}

UserPermissionManager.prototype.make_filter_controls = function() {
	let me = this;
	let row1 = $('<div class="row" style="margin-bottom: 10px;"></div>').appendTo(this.filter_area);
	let row2 = $('<div class="row" style="margin-bottom: 10px;"></div>').appendTo(this.filter_area);

	this.user_control = frappe.ui.form.make_control({
		parent: $('<div class="col-sm-4"></div>').appendTo(row1),
		df: {
			fieldname: 'user',
			label: __('User'),
			fieldtype: 'Link',
			options: 'User',
			reqd: 1,
			get_query: () => ({ filters: { enabled: 1 } }),
			onchange: () => me.on_user_or_doctype_change(),
		},
		render_input: true,
	});

	this.allow_control = frappe.ui.form.make_control({
		parent: $('<div class="col-sm-4"></div>').appendTo(row1),
		df: {
			fieldname: 'allow',
			label: __('Doctype'),
			fieldtype: 'Link',
			options: 'DocType',
			reqd: 1,
			get_query: () => ({ filters: { issingle: 0, istable: 0 } }),
			onchange: () => me.on_allow_change(),
		},
		render_input: true,
	});

	this.values_control = frappe.ui.form.make_control({
		parent: $('<div class="col-sm-4"></div>').appendTo(row1),
		df: {
			fieldname: 'values_filter',
			label: __('Values'),
			fieldtype: 'Data',
			description: __('Type to filter the checkbox list below'),
			onchange: () => me.on_values_filter_change(),
		},
		render_input: true,
	});
	// live-filter as the user types, not just on blur/enter
	this.values_control.$input.on('input', () => {
		clearTimeout(me.debounce_timer);
		me.debounce_timer = setTimeout(() => me.on_values_filter_change(), 300);
	});

	this.apply_to_all_control = frappe.ui.form.make_control({
		parent: $('<div class="col-sm-3"></div>').appendTo(row2),
		df: {
			fieldname: 'apply_to_all_doctypes',
			label: __('Apply to All Doctypes'),
			fieldtype: 'Check',
			default: 1,
			onchange: () => me.on_apply_to_all_change(),
		},
		render_input: true,
	});
	this.apply_to_all_control.set_value(1);

	this.applicable_for_control = frappe.ui.form.make_control({
		parent: $('<div class="col-sm-3 upm-applicable-for"></div>').appendTo(row2),
		df: {
			fieldname: 'applicable_for',
			label: __('Applicable For'),
			fieldtype: 'Link',
			options: 'DocType',
			get_query: () => ({
				query: 'frappe.core.doctype.user_permission.user_permission.get_applicable_for_doctype_list',
				doctype: me.allow_control.get_value(),
			}),
			onchange: () => me.on_user_or_doctype_change(),
		},
		render_input: true,
	});

	this.hide_descendants_control = frappe.ui.form.make_control({
		parent: $('<div class="col-sm-3 upm-hide-descendants"></div>').appendTo(row2),
		df: {
			fieldname: 'hide_descendants',
			label: __('Hide Descendants'),
			fieldtype: 'Check',
		},
		render_input: true,
	});
	this.hide_descendants_control.$wrapper.hide();

	this.is_default_control = frappe.ui.form.make_control({
		parent: $('<div class="col-sm-3"></div>').appendTo(row2),
		df: {
			fieldname: 'is_default',
			label: __('Is Default'),
			fieldtype: 'Check',
			description: __('Only allowed when adding a single new permission'),
		},
		render_input: true,
	});

	this.on_apply_to_all_change();
};

UserPermissionManager.prototype.make_grid_control = function() {
	let me = this;
	this.grid_control = frappe.ui.form.make_control({
		parent: this.grid_wrapper,
		df: {
			fieldname: 'for_values',
			fieldtype: 'MultiCheck',
			select_all: true,
			columns: '15rem',
			get_data: () => me.fetch_grid_options(),
		},
		render_input: true,
	});
};

UserPermissionManager.prototype.make_save_button = function() {
	let me = this;
	this.page.set_primary_action(__('Save'), () => me.save(), 'save');
};

UserPermissionManager.prototype.on_allow_change = function() {
	let allow = this.allow_control.get_value();
	let is_nested_set = allow && frappe.boot.nested_set_doctypes.includes(allow);
	this.hide_descendants_control.$wrapper.toggle(!!is_nested_set);
	if (!is_nested_set) {
		this.hide_descendants_control.set_value(0);
	}
	this.on_user_or_doctype_change();
};

UserPermissionManager.prototype.on_apply_to_all_change = function() {
	let apply_to_all = this.apply_to_all_control.get_value();
	let $wrap = this.applicable_for_control.$wrapper;
	if (cint(apply_to_all)) {
		$wrap.hide();
		this.applicable_for_control.set_value('');
	} else {
		$wrap.show();
	}
	this.on_user_or_doctype_change();
};

UserPermissionManager.prototype.on_values_filter_change = function() {
	this.values_filter = this.values_control.get_value() || '';
	// Narrowing/widening the visible rows shouldn't discard clicks the user
	// already made in this same scope.
	this.preserve_checked_on_next_fetch = true;
	this.grid_control.refresh();
};

UserPermissionManager.prototype.get_current_scope = function() {
	// Filter controls may not be constructed yet: ControlMultiCheck fetches its
	// initial options synchronously from its own constructor, before
	// make_filter_controls() has run.
	if (!this.user_control) {
		return { user: null, allow: null, applicable_for: null, apply_to_all_doctypes: 1 };
	}
	return {
		user: this.user_control.get_value(),
		allow: this.allow_control.get_value(),
		applicable_for: this.applicable_for_control.get_value() || null,
		apply_to_all_doctypes: cint(this.apply_to_all_control.get_value()),
	};
};

UserPermissionManager.prototype.on_user_or_doctype_change = function() {
	let me = this;
	let token = ++this.scope_token;
	let scope = this.get_current_scope();
	if (!scope.user || !scope.allow) {
		this.original_checked = [];
		this.grid_control.refresh();
		return;
	}

	frappe.call({
		method: 'rf.api.get_user_permission_manager_data',
		args: scope,
		callback: (r) => {
			if (token !== me.scope_token) return; // scope changed again before this returned
			me.original_checked = r.message || [];
			me.grid_control.refresh();
		},
	});
};

UserPermissionManager.prototype.fetch_grid_options = function() {
	let me = this;
	let token = this.scope_token;
	let scope = this.get_current_scope();
	if (!scope.user || !scope.allow) {
		this.cap_note.hide();
		return [];
	}

	// Only the Values-filter path opts into preserving in-flight checkbox state
	// (narrowing/widening visible rows shouldn't discard clicks). A scope change
	// or a post-save refresh must NOT preserve stale DOM state — original_checked
	// is the authoritative truth in both of those cases. One-shot: consumed and
	// cleared here so it doesn't leak into the next, unrelated refresh.
	let in_flight_checked = [];
	if (this.preserve_checked_on_next_fetch) {
		in_flight_checked = (this.grid_control.get_checked_options && this.grid_control.get_checked_options()) || [];
		this.preserve_checked_on_next_fetch = false;
	}

	let filters = [];
	if (this.values_filter) {
		filters.push([scope.allow, 'name', 'like', `%${this.values_filter}%`]);
	}

	return frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: scope.allow,
			filters: filters,
			fields: ['name'],
			limit_page_length: 100,
			order_by: 'name asc',
		},
	}).then((r) => {
		if (token !== me.scope_token) return []; // scope changed while this was in flight
		let rows = r.message || [];
		this.cap_note.toggle(rows.length === 100);
		return rows.map((row) => ({
			label: row.name,
			value: row.name,
			checked: me.original_checked.includes(row.name) || in_flight_checked.includes(row.name),
		}));
	});
};

UserPermissionManager.prototype.save = function() {
	let me = this;
	let scope = this.get_current_scope();
	if (!scope.user || !scope.allow) {
		frappe.msgprint(__('Please select a User and a Doctype first.'));
		return;
	}

	let checked_now = this.grid_control.get_checked_options();
	let to_add = checked_now.filter((v) => !this.original_checked.includes(v));
	let to_remove = this.original_checked.filter((v) => !checked_now.includes(v));

	if (!to_add.length && !to_remove.length) {
		frappe.show_alert({ message: __('No changes to save'), indicator: 'blue' });
		return;
	}

	let is_default = cint(this.is_default_control.get_value());
	if (is_default && to_add.length > 1) {
		frappe.msgprint(__('Is Default can only be applied when adding a single new permission. Please uncheck Is Default or add only one new value.'));
		return;
	}

	let do_save = () => {
		frappe.call({
			method: 'rf.api.save_user_permission_manager_selection',
			args: {
				user: scope.user,
				allow: scope.allow,
				to_add: to_add,
				to_remove: to_remove,
				applicable_for: scope.applicable_for,
				apply_to_all_doctypes: scope.apply_to_all_doctypes,
				hide_descendants: cint(me.hide_descendants_control.get_value()),
				is_default: is_default,
			},
			freeze: true,
			freeze_message: __('Saving...'),
			callback: (r) => {
				let msg = r.message || {};
				let skipped = msg.skipped || [];

				// Rows the server skipped were never persisted — drop them back
				// out of the checked state so the next diff/reload doesn't think
				// they're already saved (and leave their checkbox unchecked).
				let persisted = checked_now.filter((v) => !skipped.some((s) => s.value === v));
				me.original_checked = persisted;
				me.grid_control.refresh();

				frappe.show_alert({
					message: __('Added {0}, removed {1}', [msg.added || 0, msg.removed || 0]),
					indicator: 'green',
				});

				if (skipped.length) {
					// s.value is user-entered data and must be escaped; s.reason is a
					// server-generated message that may legitimately embed a doc link
					// (e.g. via frappe.get_desk_link), so it's rendered as-is.
					let reasons = skipped.map((s) => `<li><b>${frappe.utils.escape_html(s.value)}</b>: ${s.reason}</li>`).join('');
					frappe.msgprint({
						title: __('Some permissions were skipped'),
						indicator: 'orange',
						message: `<p>${__('{0} permission(s) could not be saved:', [skipped.length])}</p><ul>${reasons}</ul>`,
					});
				}
			},
		});
	};

	if (to_remove.length) {
		frappe.confirm(
			__('This will remove {0} existing permission(s) for this user. Continue?', [to_remove.length]),
			do_save
		);
	} else {
		do_save();
	}
};
