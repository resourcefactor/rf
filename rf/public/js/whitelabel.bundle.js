// Whitelabel JavaScript for Frappe v16
// Copyright (c) 2025, Resource Factors

console.log('[RF Whitelabel] Whitelabel script loaded');

(function() {
    'use strict';

    // Wait for frappe to be available
    function waitForFrappe(callback) {
        if (typeof frappe !== 'undefined') {
            callback();
        } else {
            setTimeout(function() { waitForFrappe(callback); }, 50);
        }
    }

    waitForFrappe(function() {
        console.log('[RF Whitelabel] Frappe object found, initializing...');

        // Set up when DOM is ready
        $(document).ready(function() {
            console.log('[RF Whitelabel] DOM ready');

            // Apply whitelabel settings if available
            if (frappe.boot.whitelabel_setting) {
                var settings = frappe.boot.whitelabel_setting;
                console.log('[RF Whitelabel] Whitelabel settings loaded');

                // Show help menu if configured
                if (settings.show_help_menu) {
                    $('.dropdown-help').attr('style', 'display: block !important');
                }

                // Apply navbar background color
                if (settings.navbar_background_color) {
                    $('.navbar').css('background-color', settings.navbar_background_color);
                }

                // Add custom navbar title
                if (settings.use_custom_navbar_title && settings.custom_navbar_title) {
                    var titleStyle = settings.custom_navbar_title_style || '';
                    var titleHtml = '<span style="' + titleStyle.replace('\n', '') + '" class="custom-navbar-title hidden-xs hidden-sm">' + settings.custom_navbar_title + '</span>';
                    $(titleHtml).insertAfter("#navbar-breadcrumbs");
                }
            }

            // Customize user display if logged in
            if (frappe.session.user && frappe.session.user !== 'Guest') {
                // Wait for toolbar setup
                $(document).on('toolbar_setup', function() {
                    setTimeout(updateUserDisplay, 100);
                });

                // Also try after a delay in case toolbar_setup already fired
                setTimeout(updateUserDisplay, 1000);
            }

            // Replace ERPNext branding with ERP in UI
            replaceERPNextBranding();

            // Watch for dynamic content changes
            observeDOMChanges();
        });
    });

    function updateUserDisplay() {
        try {
            var settings = frappe.boot.whitelabel_setting;

            // Skip if customization is disabled
            if (!settings || !settings.customize_user_display) {
                return;
            }

            var full_name = frappe.boot.user.full_name || frappe.session.user;
            var names = full_name.trim().split(/\s+/);
            var display_name = '';

            // Format based on settings
            var format = settings.user_display_format || "First + Last Initial";

            if (format === "Initials") {
                // Just initials (default Frappe behavior)
                return;
            } else if (format === "First + Last Initial") {
                if (names.length > 1) {
                    display_name = names[0] + ' ' + names[names.length - 1].charAt(0).toUpperCase();
                } else {
                    display_name = names[0];
                }
            } else if (format === "Full Name") {
                display_name = full_name;
            }

            console.log('[RF Whitelabel] Updating user display to:', display_name);

            // Find the navbar user button (v16 structure)
            var $userButton = $('.navbar .dropdown-navbar-user > .btn-reset.nav-link');

            if ($userButton.length === 0) {
                // Fallback: try alternative selector
                $userButton = $('.navbar .dropdown-navbar-user button').first();
            }

            if ($userButton.length === 0) {
                console.log('[RF Whitelabel] Could not find user button');
                return;
            }

            // Clear button and add formatted name
            $userButton.empty();

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
            console.log('[RF Whitelabel] User display updated successfully');
        } catch (e) {
            console.error('[RF Whitelabel] Error updating user display:', e);
        }
    }

    function replaceERPNextBranding() {
        /**
         * Replace "ERPNext" with "ERP" in visible UI elements
         * Only replaces display text, not IDs or data attributes
         */
        try {
            // Replace in workspace sidebar titles
            $('.sidebar-menu .workspace-link-title').each(function() {
                var $this = $(this);
                var text = $this.text();
                if (text.includes('ERPNext')) {
                    $this.text(text.replace(/ERPNext/g, 'ERP'));
                    console.log('[RF Whitelabel] Replaced workspace title:', text, '->', $this.text());
                }
            });

            // Replace in page titles
            $('.page-title').each(function() {
                var $this = $(this);
                var text = $this.text();
                if (text.includes('ERPNext')) {
                    $this.text(text.replace(/ERPNext/g, 'ERP'));
                }
            });

            // Replace in breadcrumbs (but not URLs/routes)
            $('.breadcrumb-item').each(function() {
                var $this = $(this);
                var $link = $this.find('a');
                if ($link.length) {
                    // Only replace the text, not the href
                    var text = $link.text();
                    if (text.includes('ERPNext')) {
                        $link.text(text.replace(/ERPNext/g, 'ERP'));
                    }
                } else {
                    var text = $this.text();
                    if (text.includes('ERPNext')) {
                        $this.text(text.replace(/ERPNext/g, 'ERP'));
                    }
                }
            });

            console.log('[RF Whitelabel] ERPNext branding replacement completed');
        } catch (e) {
            console.error('[RF Whitelabel] Error replacing ERPNext branding:', e);
        }
    }

    function observeDOMChanges() {
        /**
         * Watch for DOM changes and replace ERPNext branding in dynamically loaded content
         */
        try {
            var observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length) {
                        // Re-run branding replacement for newly added content
                        setTimeout(replaceERPNextBranding, 100);
                    }
                });
            });

            // Observe the main container
            var container = document.querySelector('body');
            if (container) {
                observer.observe(container, {
                    childList: true,
                    subtree: true
                });
                console.log('[RF Whitelabel] DOM observer started');
            }
        } catch (e) {
            console.error('[RF Whitelabel] Error setting up DOM observer:', e);
        }
    }

    // Make functions available globally for debugging
    window.rfUpdateUserDisplay = updateUserDisplay;
    window.rfReplaceERPNextBranding = replaceERPNextBranding;
})();
