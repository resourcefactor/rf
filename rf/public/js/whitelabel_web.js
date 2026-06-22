(function () {
	'use strict';

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}

	function init() {
		const isLoginPage =
			window.location.pathname === '/login' ||
			document.body.classList.contains('for-login') ||
			!!document.querySelector('.login-content');

		if (!isLoginPage) return;

		fetch('/api/method/rf.api.get_login_logo_url', {
			method: 'GET',
			headers: { 'Content-Type': 'application/json' },
		})
			.then((r) => r.json())
			.then((data) => {
				const url = data && data.message && data.message.login_logo_url;
				if (url) {
					replaceLoginLogo(url);
				}
			})
			.catch(() => {});
	}

	function replaceLoginLogo(url) {
		const selectors = [
			'img.app-logo',
			'.app-logo img',
			'.login-content img',
			'.page-card-body img',
			'.page-card img',
		];

		for (const selector of selectors) {
			document.querySelectorAll(selector).forEach((img) => {
				if (img && img.src && !img.closest('.navbar') && !img.closest('nav')) {
					img.src = url;
					img.style.maxWidth = '400px';
					img.style.maxHeight = '150px';
					img.style.width = 'auto';
					img.style.height = 'auto';
					img.style.objectFit = 'contain';
				}
			});
		}
	}
})();
