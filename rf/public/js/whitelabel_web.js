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

            // Fetch login logo URL from API and replace logo
            fetch('/api/method/rf.api.get_login_logo_url', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': frappe?.csrf_token || ''
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data && data.message && data.message.login_logo_url) {
                    console.log('[RF Whitelabel Web] Login logo URL from API:', data.message.login_logo_url);
                    replaceLoginLogo(data.message.login_logo_url);
                } else {
                    console.log('[RF Whitelabel Web] No login logo URL configured, using default');
                    fixLoginLogoStyles();
                }
            })
            .catch(error => {
                console.error('[RF Whitelabel Web] Error fetching login logo URL:', error);
                fixLoginLogoStyles();
            });

            // Watch for logo changes (in case Frappe updates it dynamically)
            const observer = new MutationObserver(() => {
                // Re-fetch and replace logo when DOM changes
                init();
            });
            const targetNode = document.querySelector('.page-card') || document.body;
            observer.observe(targetNode, { childList: true, subtree: true });
        } else {
            console.log('[RF Whitelabel Web] Not a login page, skipping');
        }
    }

    function replaceLoginLogo(loginLogoUrl) {
        // Find the main login page logo (exclude navbar logos)
        const logoSelectors = [
            '.login-content img.app-logo',
            '.page-card-body img.app-logo',
            '.login-content .app-logo img',
            '.page-card img.app-logo'
        ];

        let logoReplaced = false;

        logoSelectors.forEach(selector => {
            const logos = document.querySelectorAll(selector);
            logos.forEach(logo => {
                // Make sure it's not a navbar logo
                if (logo && logo.src && !logo.closest('.navbar')) {
                    console.log('[RF Whitelabel Web] Replacing login logo:', logo.src, '->', loginLogoUrl);
                    logo.src = loginLogoUrl;

                    // Apply sizing styles
                    logo.style.maxWidth = '400px';
                    logo.style.maxHeight = '150px';
                    logo.style.width = 'auto';
                    logo.style.height = 'auto';
                    logo.style.objectFit = 'contain';

                    logoReplaced = true;
                }
            });
        });

        if (!logoReplaced) {
            console.log('[RF Whitelabel Web] No login logo found to replace');
        }
    }

    function fixLoginLogoStyles() {
        // Just apply styles without changing src
        const logoSelectors = [
            '.login-content img.app-logo',
            '.page-card-body img.app-logo',
            '.login-content .app-logo img'
        ];

        logoSelectors.forEach(selector => {
            const logos = document.querySelectorAll(selector);
            logos.forEach(logo => {
                if (logo && logo.src && !logo.closest('.navbar')) {
                    logo.style.maxWidth = '400px';
                    logo.style.maxHeight = '150px';
                    logo.style.width = 'auto';
                    logo.style.height = 'auto';
                    logo.style.objectFit = 'contain';
                }
            });
        });
    }
})();
