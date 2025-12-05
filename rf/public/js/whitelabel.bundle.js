// Immediate execution to test if file is loaded
console.log('[RF Whitelabel] ========================================');
console.log('[RF Whitelabel] whitelabel.js file loaded successfully');
console.log('[RF Whitelabel] ========================================');

// Wait for frappe to be available and set up overrides
(function() {
    'use strict';

    console.log('[RF Whitelabel] Starting initialization...');

    // Check if frappe is available, if not wait
    function waitForFrappe(callback) {
        if (typeof frappe !== 'undefined') {
            callback();
        } else {
            console.log('[RF Whitelabel] Waiting for frappe object...');
            setTimeout(function() { waitForFrappe(callback); }, 50);
        }
    }

    waitForFrappe(function() {
        console.log('[RF Whitelabel] Frappe object found!');

        // Note: NOT overriding frappe.get_abbr to avoid affecting notifications
        // We'll update the navbar user display directly via DOM manipulation

        // Set up the rest when DOM and frappe are ready
        $(document).ready(function() {
            console.log('[RF Whitelabel] DOM ready, setting up...');
            console.log('[RF Whitelabel] Session user:', frappe.session.user);
            console.log('[RF Whitelabel] Boot user:', frappe.boot.user);

            if (frappe.boot.whitelabel_setting) {
                console.log('[RF Whitelabel] Whitelabel settings found');
                console.log('[RF Whitelabel] Settings:', frappe.boot.whitelabel_setting);

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

                // Log logo URLs for debugging
                console.log('[RF Whitelabel] Navbar logo:', frappe.boot.whitelabel_setting.navbar_logo);
                console.log('[RF Whitelabel] Login logo:', frappe.boot.whitelabel_setting.login_page_logo);
                console.log('[RF Whitelabel] Splash logo:', frappe.boot.whitelabel_setting.splash_page_logo);
                console.log('[RF Whitelabel] Favicon:', frappe.boot.whitelabel_setting.favicon);
            } else {
                console.log('[RF Whitelabel] WARNING: Whitelabel settings not found in boot');
            }

            // Update user display format: Full first name + Last name initial
            if (frappe.session.user && frappe.session.user !== 'Guest') {
                console.log('[RF Whitelabel] Setting up user display...');

                // V15: Wait for navbar to be fully rendered
                // The toolbar_setup event is fired after navbar is created
                $(document).on('toolbar_setup', function() {
                    console.log('[RF Whitelabel] toolbar_setup event fired');
                    // Give it a moment for DOM to settle
                    setTimeout(updateUserDisplay, 100);
                });

                // Also try after a delay in case toolbar_setup already fired
                setTimeout(function() {
                    console.log('[RF Whitelabel] Running delayed updateUserDisplay...');
                    updateUserDisplay();
                }, 1000);
            } else {
                console.log('[RF Whitelabel] Guest user detected, skipping user display setup');
            }
        });
    });

    function updateUserDisplay() {
        try {
            if (!frappe.session.user || frappe.session.user === 'Guest') {
                console.log('[RF Whitelabel] Skipping - Guest user');
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

            console.log('[RF Whitelabel] updateUserDisplay - full_name:', full_name, 'display_name:', display_name);

            // V15 Structure: Find the navbar user button
            // In V15, the structure is: <li class="dropdown-navbar-user"> -> <button class="btn-reset nav-link">
            var $userButton = $('.navbar .dropdown-navbar-user > .btn-reset.nav-link');

            if ($userButton.length === 0) {
                console.log('[RF Whitelabel] User button not found with V15 selector, trying alternatives...');

                // Alternative: look for any button in dropdown-navbar-user
                $userButton = $('.navbar .dropdown-navbar-user button').first();

                if ($userButton.length === 0) {
                    console.log('[RF Whitelabel] ERROR: Could not find user button in navbar');
                    console.log('[RF Whitelabel] Navbar HTML:', $('.navbar').html().substring(0, 500));
                    return;
                }
            }

            console.log('[RF Whitelabel] Found user button:', $userButton[0]);
            console.log('[RF Whitelabel] Current button HTML:', $userButton.html().substring(0, 200));

            // Check if button already has text, or just avatar
            var hasAvatar = $userButton.find('.avatar, .avatar-frame').length > 0;
            var currentText = $userButton.text().trim();

            console.log('[RF Whitelabel] Has avatar:', hasAvatar, 'Current text:', currentText);

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

            console.log('[RF Whitelabel] Updated button HTML:', $userButton.html());
            console.log('[RF Whitelabel] updateUserDisplay completed successfully');
        } catch (e) {
            console.error('[RF Whitelabel] Error in updateUserDisplay:', e);
            console.error('[RF Whitelabel] Stack trace:', e.stack);
        }
    }

    // Make updateUserDisplay available globally for debugging
    window.rfUpdateUserDisplay = updateUserDisplay;
    console.log('[RF Whitelabel] updateUserDisplay function exported to window.rfUpdateUserDisplay for debugging');
})();
