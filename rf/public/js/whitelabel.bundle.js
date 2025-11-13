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

                if (frappe.boot.whitelabel_setting.show_help_menu) {
                    $('.dropdown-help').attr('style', 'display: block !important');
                }
                if (frappe.boot.whitelabel_setting.logo_width) {
                    $('.app-logo').css('width',frappe.boot.whitelabel_setting.logo_width+'px');
                }
                if (frappe.boot.whitelabel_setting.logo_height) {
                    $('.app-logo').css('height',frappe.boot.whitelabel_setting.logo_height+'px');
                }
                if (frappe.boot.whitelabel_setting.navbar_background_color) {
                    $('.navbar').css('background-color',frappe.boot.whitelabel_setting.navbar_background_color)
                }
                if (frappe.boot.whitelabel_setting.custom_navbar_title_style && frappe.boot.whitelabel_setting.custom_navbar_title) {
                    $(`<span style=${frappe.boot.whitelabel_setting.custom_navbar_title_style.replace('\n','')} class="hidden-xs hidden-sm">${frappe.boot.whitelabel_setting.custom_navbar_title}</span>`).insertAfter("#navbar-breadcrumbs")
                }
            } else {
                console.log('[RF Whitelabel] WARNING: Whitelabel settings not found in boot');
            }

            // Update user display format: Full first name + Last name initial
            if (frappe.session.user && frappe.session.user !== 'Guest') {
                console.log('[RF Whitelabel] Setting up user display...');

                // Initial update with delay to ensure elements are rendered
                setTimeout(function() {
                    console.log('[RF Whitelabel] Running initial updateUserDisplay...');
                    updateUserDisplay();
                }, 500);

                // Update after toolbar loads
                $(document).on('toolbar_setup', function() {
                    console.log('[RF Whitelabel] toolbar_setup event fired');
                    setTimeout(updateUserDisplay, 100);
                });

                // Use mutation observer to handle dynamic updates
                setTimeout(function() {
                    var observer = new MutationObserver(function(mutations) {
                        console.log('[RF Whitelabel] DOM mutation detected');
                        updateUserDisplay();
                    });
                    var navbarRight = document.querySelector('.navbar-right');
                    if (navbarRight) {
                        console.log('[RF Whitelabel] Observing navbar-right');
                        observer.observe(navbarRight, { childList: true, subtree: true });
                    } else {
                        console.log('[RF Whitelabel] WARNING: navbar-right not found');
                    }
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

            // ONLY update the navbar user display (top-right corner)
            // Be very specific to avoid changing notifications and other areas

            // Target 1: The main navbar user dropdown text
            var $navbarUser = $('.navbar-right #toolbar-user').find('> a > .ellipsis, > a > span.user-name').first();
            if ($navbarUser.length) {
                console.log('[RF Whitelabel] Updating navbar user dropdown:', $navbarUser[0]);
                $navbarUser.text(display_name);
            }

            // Target 2: Alternative selector for navbar user
            var $navbarUserAlt = $('.navbar .dropdown-navbar-user > a').find('.ellipsis, .user-name').first();
            if ($navbarUserAlt.length) {
                console.log('[RF Whitelabel] Updating navbar user (alt):', $navbarUserAlt[0]);
                $navbarUserAlt.text(display_name);
            }

            // Target 3: User display next to avatar in top-right
            var $avatarText = $('.navbar-right').find('.avatar').next('.ellipsis, .user-name').first();
            if ($avatarText.length) {
                console.log('[RF Whitelabel] Updating avatar text:', $avatarText[0]);
                $avatarText.text(display_name);
            }

            console.log('[RF Whitelabel] updateUserDisplay completed');
        } catch (e) {
            console.error('[RF Whitelabel] Error in updateUserDisplay:', e);
        }
    }

    // Make updateUserDisplay available globally for debugging
    window.rfUpdateUserDisplay = updateUserDisplay;
    console.log('[RF Whitelabel] updateUserDisplay function exported to window.rfUpdateUserDisplay for debugging');
})();
