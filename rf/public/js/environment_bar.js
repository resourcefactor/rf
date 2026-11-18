// Environment bar: a full-width strip across the top of the desk that says which site this is
// (STAGING, UAT, ...), set in RF Settings > Environment. rf.environment resolves the label and
// colours server-side and ships them as `frappe.boot.rf_environment` (null on production, which has
// no bar).
//
// Runs once at load, before the desk renders, so the shell never lays out without the bar. The
// layout itself is in environment_bar.bundle.css, keyed on the `rf-env-bar-on` class added here.
(function () {
	"use strict";

	if (typeof frappe === "undefined" || !frappe.boot) return;

	const env = frappe.boot.rf_environment;
	if (!env || document.querySelector(".rf-env-bar")) return;

	const root = document.documentElement;
	// CSSOM setters drop a value that isn't a valid colour rather than injecting it.
	root.style.setProperty("--rf-env-bar-bg", env.color);
	root.style.setProperty("--rf-env-bar-fg", env.text_color);

	const bar = document.createElement("div");
	bar.className = "rf-env-bar";
	bar.setAttribute("role", "status");
	bar.title = __("This is the {0} site ({1})", [__(env.environment), frappe.boot.sitename]);
	const text = document.createElement("span");
	text.className = "rf-env-bar-text";
	text.textContent = env.label;
	bar.appendChild(text);

	document.body.prepend(bar);
	root.classList.add("rf-env-bar-on");

	// Mobile browsers paint their own address bar from theme-color: match it to the bar.
	document
		.querySelectorAll('meta[name="theme-color"]')
		.forEach((meta) => meta.setAttribute("content", env.color));
})();
