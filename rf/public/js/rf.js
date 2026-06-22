(function () {
	'use strict';

	function getSettings() {
		return (frappe.boot && frappe.boot.rf_settings) || {};
	}

	function injectHelpMenuCSS() {
		if (!getSettings().hide_help_menu) return;
		if (document.getElementById('rf-hide-help-css')) return;
		const style = document.createElement('style');
		style.id = 'rf-hide-help-css';
		// Hide top navbar help dropdown + its vertical separator bar
		style.textContent = '.dropdown-help, .navbar .vertical-bar { display: none !important; }';
		document.head.appendChild(style);
	}

	function applyNavbarColor() {
		const color = getSettings().navbar_background_color;
		if (color) {
			$('.navbar').css('background-color', color);
		}
	}

	function applyNavbarTitle() {
		const settings = getSettings();
		if (!settings.custom_navbar_title) return;
		if ($('#navbar-breadcrumbs').length && $('#rf-navbar-title').length === 0) {
			const style = (settings.custom_navbar_title_style || '').replace(/\n/g, ' ');
			$(`<span id="rf-navbar-title" style="${style}" class="hidden-xs hidden-sm">${settings.custom_navbar_title}</span>`).insertAfter('#navbar-breadcrumbs');
		}
	}

	function updateUserDisplay() {
		try {
			if (!frappe.session.user || frappe.session.user === 'Guest') return;

			const full_name =
				frappe.boot.user.full_name ||
				(frappe.boot.user.first_name
					? frappe.boot.user.first_name + (frappe.boot.user.last_name ? ' ' + frappe.boot.user.last_name : '')
					: '') ||
				'';

			if (!full_name) return;

			const names = full_name.trim().split(/\s+/);
			const display_name =
				names.length > 1
					? names[0] + ' ' + names[names.length - 1].charAt(0).toUpperCase()
					: names[0];

			// v16 DOM: .navbar .avatar inside a .nav-link
			const $avatar = $('.navbar .avatar');
			if (!$avatar.length) return;
			const $navLink = $avatar.closest('.nav-link');
			if (!$navLink.length) return;

			$avatar.hide();
			if ($navLink.find('.rf-user-name').length === 0) {
				$navLink.append(
					`<span class="rf-user-name" style="display:inline-block;padding:6px 10px;background:var(--dark-green-avatar-bg,#2c4e2e);color:var(--dark-green-avatar-color,#fff);border-radius:4px;font-size:14px;font-weight:500;white-space:nowrap;">${display_name}</span>`
				);
			}
		} catch (e) {
			// ignore
		}
	}

	function relabelSidebar() {
		try {
			const $title = $('.sidebar-header .sidebar-item-label.header-subtitle');
			if ($title.length && $title.text().trim() !== 'ERP') {
				$title.text('ERP');
			}
		} catch (e) {
			// ignore
		}
	}

	function runCustomizations() {
		injectHelpMenuCSS();
		applyNavbarColor();
		applyNavbarTitle();
		updateUserDisplay();
		relabelSidebar();
	}

	function init() {
		// Inject CSS immediately — persists across all DOM rebuilds, no timing issues
		injectHelpMenuCSS();

		// toolbar_setup fires after Frappe renders the navbar + sidebar header DOM
		$(document).one('toolbar_setup', () => {
			runCustomizations();
			$(document).on('page-change', () => setTimeout(runCustomizations, 200));

			let timeout;
			const observer = new MutationObserver(() => {
				clearTimeout(timeout);
				timeout = setTimeout(runCustomizations, 150);
			});
			observer.observe(document.body, { childList: true, subtree: true });
		});
	}

	function waitForFrappeReady(cb, attempts = 50) {
		if (typeof frappe !== 'undefined' && frappe.boot && frappe.user) {
			cb();
		} else if (attempts > 0) {
			setTimeout(() => waitForFrappeReady(cb, attempts - 1), 100);
		}
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', () => waitForFrappeReady(init));
	} else {
		waitForFrappeReady(init);
	}
})();
