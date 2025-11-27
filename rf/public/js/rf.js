$(document).ready(function () {
    // Ensure frappe is available
    if (typeof frappe === 'undefined') {
        console.error("RF App: frappe is not defined");
        return;
    }

    const run_customizations = () => {
        // 1. Hide Help Menu based on RF Settings
        frappe.db.get_single_value('RF Settings', 'hide_help_menu')
            .then(hide => {
                if (hide) {
                    // Try multiple selectors for v16/v15 compatibility
                    $('.dropdown-help').hide();
                    $('.navbar .nav-item[title="Help"]').hide();
                    $('.navbar .nav-item[data-label="Help"]').hide();
                    // Also try hiding by icon if needed, but be careful
                }
            })
            .catch(err => {
                console.warn("RF App: Could not fetch RF Settings", err);
            });

        // 2. Display Full Name instead of Initial
        try {
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
        } catch (e) {
            console.error("RF App: Error setting full name", e);
        }
    };

    // Run immediately if ready, or wait?
    // In some versions, we might need to wait for 'app_ready' or similar.
    // But usually $(document).ready is fine for DOM, but frappe.user might be populated later?
    // frappe.user is populated from frappe.boot which is usually available in desk.

    run_customizations();

    // Also listen for route changes in case the navbar is re-rendered (unlikely for navbar, but good practice)
    // $(document).on('page-change', function() {
    //     run_customizations();
    // });
});
