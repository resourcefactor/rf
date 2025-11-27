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
                    // Selectors for Help Menu
                    const helpSelectors = [
                        '.dropdown-help',
                        '.navbar .nav-item[title="Help"]',
                        '.navbar .nav-item[data-label="Help"]',
                        '.navbar a[href*="help"]' // Fallback
                    ];

                    $(helpSelectors.join(',')).hide();

                    // Also hide by finding the icon if needed
                    $('.navbar .icon-help').closest('.nav-item').hide();
                }
            })
            .catch(err => {
                console.warn("RF App: Could not fetch RF Settings", err);
            });

        // 2. Display Full Name instead of Initial
        try {
            const user_name = frappe.user.full_name;

            // Find the user dropdown by looking for the avatar in the navbar
            // This is more robust than relying on a specific class like .dropdown-user which might have changed
            const $avatar = $('.navbar .avatar');

            if ($avatar.length) {
                const $navLink = $avatar.closest('.nav-link');

                if ($navLink.length) {
                    // Hide the avatar
                    $avatar.hide();

                    // Add full name if not already present
                    if ($navLink.find('.rf-user-name').length === 0) {
                        $navLink.append(`<span class="rf-user-name" style="margin-left: 8px; font-weight: 500;">${user_name}</span>`);
                    }
                }
            }
        } catch (e) {
            console.error("RF App: Error setting full name", e);
        }
    };

    // Run immediately
    run_customizations();

    // Use MutationObserver to handle dynamic rendering (common in SPAs like ERPNext)
    const observer = new MutationObserver((mutations) => {
        run_customizations();
    });

    // Start observing the navbar or body
    const targetNode = document.querySelector('.navbar') || document.body;
    if (targetNode) {
        observer.observe(targetNode, { childList: true, subtree: true });
    }
});
