// Whitelabel Web - Login Page Logo Fix
console.log('[RF Whitelabel Web] Initializing login page customization');

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        console.log('[RF Whitelabel Web] DOM ready');

        // Check if we're on the login page
        const isLoginPage = window.location.pathname === '/login' ||
                           document.body.classList.contains('for-login') ||
                           document.querySelector('.login-content') !== null;

        if (isLoginPage) {
            console.log('[RF Whitelabel Web] Login page detected, applying logo fixes');
            fixLoginLogo();

            // Watch for logo changes (in case Frappe updates it dynamically)
            const observer = new MutationObserver(fixLoginLogo);
            const targetNode = document.querySelector('.page-card') || document.body;
            observer.observe(targetNode, { childList: true, subtree: true });
        } else {
            console.log('[RF Whitelabel Web] Not a login page, skipping');
        }
    }

    function fixLoginLogo() {
        // Find all logo images on the page
        const logoSelectors = [
            '.app-logo img',
            '.login-content img',
            '.page-card img',
            'img.app-logo',
            '.login-icon-svg'
        ];

        let logoFound = false;

        logoSelectors.forEach(selector => {
            const logos = document.querySelectorAll(selector);
            logos.forEach(logo => {
                if (logo && logo.src) {
                    logoFound = true;
                    console.log('[RF Whitelabel Web] Found logo:', logo.src);

                    // Apply sizing styles directly
                    logo.style.maxWidth = '400px';
                    logo.style.maxHeight = '150px';
                    logo.style.minWidth = '200px';
                    logo.style.minHeight = '60px';
                    logo.style.width = 'auto';
                    logo.style.height = 'auto';
                    logo.style.objectFit = 'contain';

                    console.log('[RF Whitelabel Web] Applied size styles to logo');
                }
            });
        });

        if (!logoFound) {
            console.log('[RF Whitelabel Web] No logo found on page yet');
        }
    }
})();
