frappe.ready(function () {
    // 1. Hide Help Menu based on RF Settings
    frappe.db.get_single_value('RF Settings', 'hide_help_menu')
        .then(hide => {
            if (hide) {
                $('.dropdown-help').hide();
            }
        })
        .catch(err => {
            // console.log("RF Settings not accessible:", err);
        });

    // 2. Display Full Name instead of Initial
    const user_name = frappe.user.full_name;
    const $user_dropdown_link = $('.navbar .dropdown-user .nav-link');

    if ($user_dropdown_link.length) {
        // Hide the avatar (which shows initials or image)
        $user_dropdown_link.find('.avatar').hide();

        // Add full name if not already present
        if ($user_dropdown_link.find('.rf-user-name').length === 0) {
            $user_dropdown_link.append(`<span class="rf-user-name" style="margin-left: 8px; font-weight: 500;">${user_name}</span>`);
        }
    }
});
