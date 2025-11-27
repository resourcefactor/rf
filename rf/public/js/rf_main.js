// RF App main script (new file)
console.log('RF App: script loaded (new)');

function waitForFrappeReady(cb, attempts = 50) {
    if (typeof frappe !== 'undefined' && frappe.boot && frappe.user) {
        console.log('RF App: frappe is ready');
        cb();
    } else if (attempts > 0) {
        setTimeout(() => waitForFrappeReady(cb, attempts - 1), 100);
    } else {
        console.warn('RF App: frappe not ready after waiting');
    }
}

function runCustomizations() {
    console.log('RF App: runCustomizations start');
    // Hide Help Menu
    frappe.db.get_single_value('RF Settings', 'hide_help_menu')
        .then(hide => {
            console.log('RF App: hide_help_menu value', hide);
            if (hide) {
                const $helpBtn = $('button[aria-label="Help Dropdown"]');
                console.log('RF App: help button found', $helpBtn.length);
                $helpBtn.hide();
                $('.dropdown-help').hide();
                $('[title="Help"]').hide();
                $('[data-label="Help"]').hide();
            }
        })
        .catch(err => console.warn('RF App: Could not fetch RF Settings', err));

    // Display full name
    try {
        const user_name = frappe.user.full_name;
        const $avatar = $('.navbar .avatar');
        console.log('RF App: avatar found', $avatar.length);
        if ($avatar.length) {
            const $navLink = $avatar.closest('.nav-link');
            if ($navLink.length) {
                $avatar.hide();
                if ($navLink.find('.rf-user-name').length === 0) {
                    $navLink.append(`<span class="rf-user-name" style="margin-left: 8px; font-weight: 500;">${user_name}</span>`);
                    console.log('RF App: added full name span');
                }
            }
        }
    } catch (e) {
        console.error('RF App: Error setting full name', e);
    }

    // Change ERPNext to ERP
    try {
        const $sidebarTitle = $('.sidebar-header .sidebar-item-label.header-subtitle');
        console.log('RF App: sidebar title found', $sidebarTitle.length, 'text:', $sidebarTitle.text());
        if ($sidebarTitle.length && $sidebarTitle.text().trim() !== 'ERP') {
            $sidebarTitle.text('ERP');
            console.log('RF App: sidebar title changed to ERP');
        }
    } catch (e) {
        console.error('RF App: Error changing sidebar title', e);
    }
    console.log('RF App: runCustomizations end');
}

function init() {
    setTimeout(runCustomizations, 200);
    let timeout;
    const observer = new MutationObserver(() => {
        clearTimeout(timeout);
        timeout = setTimeout(runCustomizations, 150);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    $(document).on('page-change', () => setTimeout(runCustomizations, 200));
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('RF App: DOMContentLoaded');
        waitForFrappeReady(init);
    });
} else {
    console.log('RF App: document already ready');
    waitForFrappeReady(init);
}
