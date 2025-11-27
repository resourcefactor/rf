// Whitelabel JavaScript for Frappe v16
// Copyright (c) 2025, Resource Factors

(function() {
    'use strict';

    var isReplacing = false; // Flag to prevent recursive calls
    var replaceTimeout = null;

    // Wait for frappe to be available
    function waitForFrappe(callback) {
        if (typeof frappe !== 'undefined') {
            callback();
        } else {
            setTimeout(function() { waitForFrappe(callback); }, 50);
        }
    }

    waitForFrappe(function() {
        // Set up when DOM is ready
        $(document).ready(function() {

            // Apply whitelabel settings if available
            if (frappe.boot.whitelabel_setting) {
                var settings = frappe.boot.whitelabel_setting;

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
            setTimeout(replaceERPNextBranding, 100);

            // Replace again after delay for late-loading elements
            setTimeout(replaceERPNextBranding, 1500);

            // Watch for dynamic content changes (with debouncing)
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

            // Find the navbar user button (v16 structure)
            var $userButton = $('.navbar .dropdown-navbar-user > .btn-reset.nav-link');

            if ($userButton.length === 0) {
                $userButton = $('.navbar .dropdown-navbar-user button').first();
            }

            if ($userButton.length === 0) {
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
        } catch (e) {
            console.error('[RF Whitelabel] Error updating user display:', e);
        }
    }

    function replaceERPNextBranding() {
        /**
         * Replace "ERPNext" with "ERP" in visible UI elements
         * Optimized with flag to prevent recursive calls
         */
        if (isReplacing) {
            return; // Already running, skip
        }

        isReplacing = true;

        try {
            var replaced = false;

            // Replace in navbar top-left area
            $('.navbar .navbar-home, .navbar-brand').each(function() {
                var $this = $(this);
                var text = $this.text();
                if (text.includes('ERPNext')) {
                    $this.text(text.replace(/ERPNext/g, 'ERP'));
                    replaced = true;
                }
            });

            // Replace in app selector/switcher
            $('.app-selector, .app-name, .sidebar-label').each(function() {
                var $this = $(this);
                var text = $this.text();
                if (text.includes('ERPNext')) {
                    $this.text(text.replace(/ERPNext/g, 'ERP'));
                    replaced = true;
                }
            });

            // Replace in workspace sidebar titles
            $('.sidebar-menu .workspace-link-title, .sidebar-item-label, .workspace-label').each(function() {
                var $this = $(this);
                var text = $this.text();
                if (text.includes('ERPNext')) {
                    $this.text(text.replace(/ERPNext/g, 'ERP'));
                    replaced = true;
                }
            });

            // Replace in page titles
            $('.page-title, h1, h2').each(function() {
                var $this = $(this);
                var text = $this.text();
                if (text.includes('ERPNext')) {
                    $this.text(text.replace(/ERPNext/g, 'ERP'));
                    replaced = true;
                }
            });

            // Replace in breadcrumbs (but not URLs/routes)
            $('.breadcrumb-item, #navbar-breadcrumbs li').each(function() {
                var $this = $(this);
                var $link = $this.find('a');
                if ($link.length) {
                    var text = $link.text();
                    if (text.includes('ERPNext')) {
                        $link.text(text.replace(/ERPNext/g, 'ERP'));
                        replaced = true;
                    }
                } else {
                    var text = $this.text();
                    if (text.includes('ERPNext')) {
                        $this.text(text.replace(/ERPNext/g, 'ERP'));
                        replaced = true;
                    }
                }
            });

            // Generic: Replace in any visible text that contains ERPNext
            $('*').not('script, style, [data-route], [href], [src]').each(function() {
                var childNodes = this.childNodes;
                for (var i = 0; i < childNodes.length; i++) {
                    var node = childNodes[i];
                    if (node.nodeType === 3) { // Text node
                        var text = node.nodeValue;
                        if (text && text.includes('ERPNext')) {
                            node.nodeValue = text.replace(/ERPNext/g, 'ERP');
                            replaced = true;
                        }
                    }
                }
            });
        } catch (e) {
            console.error('[RF Whitelabel] Error replacing ERPNext branding:', e);
        } finally {
            isReplacing = false;
        }
    }

    function observeDOMChanges() {
        /**
         * Watch for DOM changes with debouncing to prevent excessive calls
         */
        try {
            var observer = new MutationObserver(function(mutations) {
                // Debounce: only run once every 500ms
                if (replaceTimeout) {
                    clearTimeout(replaceTimeout);
                }

                replaceTimeout = setTimeout(function() {
                    replaceERPNextBranding();
                }, 500);
            });

            // Observe only the main content area, not the entire body
            var container = document.querySelector('.main-section') || document.querySelector('body');
            if (container) {
                observer.observe(container, {
                    childList: true,
                    subtree: true
                });
            }
        } catch (e) {
            console.error('[RF Whitelabel] Error setting up DOM observer:', e);
        }
    }

    // Make functions available globally for debugging
    window.rfUpdateUserDisplay = updateUserDisplay;
    window.rfReplaceERPNextBranding = replaceERPNextBranding;
})();
