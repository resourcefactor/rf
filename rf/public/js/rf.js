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
                    // Try to find the Help icon and hide its parent container
                    // The icon usually has class 'icon-help' or similar SVG usage
                    const $helpIcon = $('.navbar use[href*="help"]').closest('svg');
                    if ($helpIcon.length) {
                        $helpIcon.closest('.nav-item').hide();
                        $helpIcon.closest('li').hide();
                    }

                    // Fallback selectors
                    $('.dropdown-help').hide();
                    $('[title="Help"]').hide();
                    $('[data-label="Help"]').hide();
                }
            })
            .catch(err => {
                // console.warn("RF App: Could not fetch RF Settings", err);
            });

        // 2. Display Full Name instead of Initial
        try {
            const user_name = frappe.user.full_name;

            // Find the user dropdown by looking for the avatar in the navbar
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

        // 3. Change "ERPNext" to "ERP" in Sidebar Header
        try {
            // Use a more specific selector and force it
            const $sidebarTitle = $('.sidebar-header .sidebar-item-label.header-subtitle');
            if ($sidebarTitle.length && $sidebarTitle.text().trim() !== 'ERP') {
                $sidebarTitle.text('ERP');
            }
        } catch (e) {
            console.error("RF App: Error changing sidebar title", e);
        }
    };

    // Run immediately
    run_customizations();

    // Use MutationObserver to handle dynamic rendering
    // Debounce the observer to avoid performance issues and ensure DOM is settled
    let timeout;
    const observer = new MutationObserver((mutations) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            run_customizations();
        }, 100);
    });

    // Start observing the body for changes
    observer.observe(document.body, { childList: true, subtree: true });

    // Also run on page change events if any
    $(document).on('page-change', function () {
        setTimeout(run_customizations, 200);
    });
});
