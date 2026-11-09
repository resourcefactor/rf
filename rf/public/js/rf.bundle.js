// RF white-label patches for the v16 desk.
//
// Loaded through app_include_js (as a hashed bundle, so deploys are never served stale), after
// desk.bundle.js, so the classes patched here already exist
// and `frappe.boot` is set (desk.html inlines it). Everything runs once at load: no polling and no
// MutationObserver. App renames (ERPNext -> ERP, ...) are not done here -- they ship as
// rf/translations/en.csv, which every `__()` render picks up. Help rows from Navbar Settings are
// hidden or restricted to System Managers in the DB by rf.whitelabel.
(function () {
	"use strict";

	if (typeof frappe === "undefined" || !frappe.boot) return;

	const settings = frappe.boot.rf_settings || {};
	if (!settings.hide_help_menu) return;

	// Turns on the catch-all in whitelabel_app.bundle.css that hides any remaining link to a vendor
	// domain (docs, forum, support, Frappe Cloud).
	document.documentElement.classList.add("rf-hide-vendor-links");

	// Help submenu: drop the per-page docs links (frappe's and ERPNext's help_links.js, which
	// point at docs.frappe.io / erpnext.com). With these gone and the vendor Navbar rows hidden,
	// the sidebar header menu draws no Help row at all for non-admins. The dock's header menu
	// is built by the same class, so it is covered too.
	if (frappe.ui.SidebarHeader) {
		frappe.ui.SidebarHeader.prototype.get_custom_help_links = () => [];
	}

	// About dialog: replace frappe's (vendor logo, frappe.io / GitHub / forum / Frappe Cloud links)
	// with a neutral one. System Managers also see the installed app versions.
	frappe.provide("frappe.ui.misc");
	frappe.ui.misc.about = function () {
		const esc = frappe.utils.escape_html;
		const app_name = frappe.boot.sysdefaults?.app_name || __("ERP");
		let versions = "";
		if (frappe.user.has_role("System Manager")) {
			const titles = {};
			(frappe.boot.app_data || []).forEach((app) => {
				titles[app.app_name] = app.app_title;
			});
			versions = Object.entries(frappe.boot.versions || {})
				.map(
					([app, version]) =>
						`<div class="flex justify-between"><span>${esc(
							__(titles[app] || app)
						)}</span><span class="text-muted">${esc(version)}</span></div>`
				)
				.join("");
		}
		const dialog = new frappe.ui.Dialog({ title: __("About") });
		$(dialog.body).html(
			`<div class="flex flex-col gap-3">
				<div class="text-lg font-semibold">${esc(app_name)}</div>
				${versions ? `<div class="flex flex-col gap-1">${versions}</div>` : ""}
			</div>`
		);
		dialog.show();
	};

	// /desk apps screen: its avatar menu hard-codes "About" and "Frappe Support"
	// (support.frappe.io) inside DesktopPage.setup_avatar. The page fires `desktop_screen` with
	// its instance just before calling that method, so wrap it there: while it runs, the one
	// Dropdown it builds for `.desktop-avatar` gets those rows filtered out. Frappe's menu code
	// is not copied, so rows it adds in future still show up.
	const HIDDEN_DESKTOP_ROWS = ["About", "Frappe Support"];
	$(document).on("desktop_screen", (e, data) => {
		const desktop = data && data.desktop;
		if (!desktop || desktop.__rf_avatar_patched) return;
		desktop.__rf_avatar_patched = true;

		const setup_avatar = desktop.setup_avatar;
		desktop.setup_avatar = function (...args) {
			const Dropdown = frappe.ui.Dropdown;
			const hidden = HIDDEN_DESKTOP_ROWS.map((label) => __(label));
			frappe.ui.Dropdown = class extends Dropdown {
				constructor(opts = {}) {
					if (Array.isArray(opts.options) && $(opts.trigger).is(".desktop-avatar")) {
						opts = {
							...opts,
							options: opts.options.filter((row) => !hidden.includes(row.label)),
						};
					}
					super(opts);
				}
			};
			try {
				return setup_avatar.apply(this, args);
			} finally {
				frappe.ui.Dropdown = Dropdown;
			}
		};
	});
})();
