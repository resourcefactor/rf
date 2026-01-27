// Wait for frappe to be available and set up overrides
(function() {
    'use strict';

    // Check if frappe is available, if not wait
    function waitForFrappe(callback) {
        if (typeof frappe !== 'undefined') {
            callback();
        } else {
            setTimeout(function() { waitForFrappe(callback); }, 50);
        }
    }

    waitForFrappe(function() {
        // Note: NOT overriding frappe.get_abbr to avoid affecting notifications
        // We'll update the navbar user display directly via DOM manipulation

        // Set up the rest when DOM and frappe are ready
        $(document).ready(function() {
            if (frappe.boot.whitelabel_setting) {
                if (frappe.boot.whitelabel_setting.show_help_menu) {
                    $('.dropdown-help').attr('style', 'display: block !important');
                }

                // Apply navbar background color
                if (frappe.boot.whitelabel_setting.navbar_background_color) {
                    $('.navbar').css('background-color',frappe.boot.whitelabel_setting.navbar_background_color)
                }

                // Apply custom navbar title
                if (frappe.boot.whitelabel_setting.custom_navbar_title_style && frappe.boot.whitelabel_setting.custom_navbar_title) {
                    $(`<span style=${frappe.boot.whitelabel_setting.custom_navbar_title_style.replace('\n','')} class="hidden-xs hidden-sm">${frappe.boot.whitelabel_setting.custom_navbar_title}</span>`).insertAfter("#navbar-breadcrumbs")
                }
            }

            // Update user display format: Full first name + Last name initial
            if (frappe.session.user && frappe.session.user !== 'Guest') {
                // V15: Wait for navbar to be fully rendered
                // The toolbar_setup event is fired after navbar is created
                $(document).on('toolbar_setup', function() {
                    // Give it a moment for DOM to settle
                    setTimeout(updateUserDisplay, 100);
                });

                // Also try after a delay in case toolbar_setup already fired
                setTimeout(function() {
                    updateUserDisplay();
                }, 1000);
            }
        });
    });

    function updateUserDisplay() {
        try {
            if (!frappe.session.user || frappe.session.user === 'Guest') {
                return;
            }

            var full_name = frappe.boot.user.full_name || frappe.session.user;
            var names = full_name.trim().split(/\s+/);
            var display_name = '';

            if (names.length > 1) {
                // Full first name + Last name initial
                display_name = names[0] + ' ' + names[names.length - 1].charAt(0).toUpperCase();
            } else {
                display_name = names[0];
            }

            // V15 Structure: Find the navbar user button
            // In V15, the structure is: <li class="dropdown-navbar-user"> -> <button class="btn-reset nav-link">
            var $userButton = $('.navbar .dropdown-navbar-user > .btn-reset.nav-link');

            if ($userButton.length === 0) {
                // Alternative: look for any button in dropdown-navbar-user
                $userButton = $('.navbar .dropdown-navbar-user button').first();

                if ($userButton.length === 0) {
                    return;
                }
            }

            // Clear the button content and rebuild it with just the name
            // Remove avatar to save space and show full name
            $userButton.empty();

            // Create span with inline styles to ensure they're applied
            // Use the same green background that Frappe uses for avatars
            var $nameSpan = $('<span class="user-name-display"></span>')
                .text(display_name)
                .css({
                    'display': 'inline-block',
                    'padding': '8px 12px',
                    'background': 'var(--dark-green-avatar-bg)',
                    'color': 'var(--dark-green-avatar-color)',
                    'border-radius': '4px',
                    'font-size': '14px',
                    'font-weight': '500',
                    'white-space': 'nowrap'
                });

            $userButton.append($nameSpan);
        } catch (e) {
            // Silently handle errors
        }
    }
})();
