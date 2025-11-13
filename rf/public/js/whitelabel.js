// Override frappe.get_abbr to show full first name + last initial
frappe.get_abbr = function(name, max_length) {
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

    return abbr;
};

$(window).on('load', function() {
    frappe.after_ajax(function () {
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

        // Update user display format: Full first name + Last name initial
        if (frappe.session.user && frappe.session.user !== 'Guest') {
            setTimeout(function() {
                updateUserDisplay();
                // Use mutation observer to handle dynamic updates
                var observer = new MutationObserver(function() {
                    updateUserDisplay();
                });
                var navbarUserSection = document.querySelector('.navbar-right');
                if (navbarUserSection) {
                    observer.observe(navbarUserSection, { childList: true, subtree: true });
                }
            }, 500);
        }
    })
})

function updateUserDisplay() {
    if (!frappe.session.user || frappe.session.user === 'Guest') return;

    var full_name = frappe.boot.user.full_name || frappe.session.user;
    var names = full_name.trim().split(/\s+/);
    var display_name = '';

    if (names.length > 1) {
        // Full first name + Last name initial
        display_name = names[0] + ' ' + names[names.length - 1].charAt(0).toUpperCase();
    } else {
        display_name = names[0];
    }

    // Update all possible user display locations
    // Top right navbar - avatar with text
    var $avatar = $('.avatar-frame, .avatar, [data-user], .user-image').parent().find('.avatar-name, .user-name, .ellipsis');
    if ($avatar.length) {
        $avatar.text(display_name);
    }

    // Navbar user text
    $('.navbar .navbar-right .nav-link .user-name').text(display_name);

    // Standard toolbar user
    $('#toolbar-user').find('.ellipsis, .user-name').each(function() {
        if ($(this).text().trim() && $(this).text().trim() !== display_name) {
            $(this).text(display_name);
        }
    });

    // Update user image title/alt attributes
    $('[data-user="' + frappe.session.user + '"]').attr('title', display_name);
    $('.user-image, .avatar-frame').attr('title', display_name);
}
