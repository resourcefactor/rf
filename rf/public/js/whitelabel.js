// Store original frappe.get_abbr
var original_get_abbr = frappe.get_abbr;

// Override frappe.get_abbr to show full first name + last initial
frappe.get_abbr = function(name, max_length) {
    console.log('[RF Whitelabel] get_abbr called with:', name, 'max_length:', max_length);

    if (!name) return "";

    var names = name.trim().split(/\s+/);
    var abbr = "";

    if (names.length > 1) {
        // Full first name + Last name initial
        abbr = names[0] + ' ' + names[names.length - 1].charAt(0).toUpperCase();
    } else {
        abbr = names[0];
    }

    // If max_length is specified and abbr is longer, truncate
    if (max_length && abbr.length > max_length) {
        abbr = abbr.substr(0, max_length);
    }

    console.log('[RF Whitelabel] get_abbr returning:', abbr);
    return abbr;
};

// Run as early as possible
frappe.ready(function() {
    console.log('[RF Whitelabel] frappe.ready fired');
    console.log('[RF Whitelabel] Session user:', frappe.session.user);
    console.log('[RF Whitelabel] Boot user:', frappe.boot.user);

    if (frappe.boot.whitelabel_setting) {
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
    }

    // Update user display format: Full first name + Last name initial
    if (frappe.session.user && frappe.session.user !== 'Guest') {
        console.log('[RF Whitelabel] Setting up user display...');

        // Initial update
        setTimeout(function() {
            updateUserDisplay();
        }, 100);

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
            }
        }, 500);
    }
})

function updateUserDisplay() {
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

    // Method 1: Find all text nodes with user name in navbar-right
    $('.navbar-right').find('*').each(function() {
        var $elem = $(this);
        var text = $elem.text().trim();
        // Only update leaf text nodes
        if ($elem.children().length === 0 && text && text !== display_name) {
            // Check if it looks like a user name (contains letters and spaces/initials)
            if (/^[A-Z\s\.]+$/i.test(text) && text.length < 50) {
                console.log('[RF Whitelabel] Updating element:', $elem[0].tagName, 'from:', text, 'to:', display_name);
                $elem.text(display_name);
            }
        }
    });

    // Method 2: Target specific known selectors
    var selectors = [
        '.navbar-right .ellipsis',
        '.navbar-right .user-name',
        '.navbar-right .avatar-name',
        '#toolbar-user .ellipsis',
        '#toolbar-user .user-name',
        '.dropdown-navbar-user .full-name',
        '.dropdown-navbar-user .user-name'
    ];

    selectors.forEach(function(selector) {
        var $elem = $(selector);
        if ($elem.length) {
            console.log('[RF Whitelabel] Found selector:', selector, 'updating to:', display_name);
            $elem.text(display_name);
        }
    });

    // Method 3: Update data attributes
    $('[data-user="' + frappe.session.user + '"]').attr('title', display_name);
    $('.user-image, .avatar-frame').attr('title', display_name);

    console.log('[RF Whitelabel] updateUserDisplay completed');
}
