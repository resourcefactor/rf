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
                var full_name = frappe.boot.user.full_name || frappe.session.user;
                var names = full_name.split(' ');
                var display_name = '';

                if (names.length > 1) {
                    // Full first name + Last name initial
                    display_name = names[0] + ' ' + names[names.length - 1].charAt(0);
                } else {
                    display_name = names[0];
                }

                // Update the navbar user display
                $('.navbar .navbar-user-section .user-info .user-name').text(display_name);

                // For mobile/dropdown view
                $('#toolbar-user .user-name-text').text(display_name);
                $('#toolbar-user a[data-label="My Profile"]').closest('.dropdown-menu').find('.user-info .user-name').text(display_name);
            }, 500);
        }
    })
})
