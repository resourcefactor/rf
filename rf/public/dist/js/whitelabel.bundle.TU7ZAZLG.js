(() => {
  // ../rf/rf/public/js/whitelabel.bundle.js
  (function() {
    "use strict";
    function waitForFrappe(callback) {
      if (typeof frappe !== "undefined") {
        callback();
      } else {
        setTimeout(function() {
          waitForFrappe(callback);
        }, 50);
      }
    }
    waitForFrappe(function() {
      $(document).ready(function() {
        if (frappe.boot.whitelabel_setting) {
          if (frappe.boot.whitelabel_setting.show_help_menu) {
            $(".dropdown-help").attr("style", "display: block !important");
          }
          if (frappe.boot.whitelabel_setting.navbar_background_color) {
            $(".navbar").css("background-color", frappe.boot.whitelabel_setting.navbar_background_color);
          }
          if (frappe.boot.whitelabel_setting.custom_navbar_title_style && frappe.boot.whitelabel_setting.custom_navbar_title) {
            $(`<span style=${frappe.boot.whitelabel_setting.custom_navbar_title_style.replace("\n", "")} class="hidden-xs hidden-sm">${frappe.boot.whitelabel_setting.custom_navbar_title}</span>`).insertAfter("#navbar-breadcrumbs");
          }
        }
        if (frappe.session.user && frappe.session.user !== "Guest") {
          $(document).on("toolbar_setup", function() {
            setTimeout(updateUserDisplay, 100);
          });
          setTimeout(function() {
            updateUserDisplay();
          }, 1e3);
        }
      });
    });
    function updateUserDisplay() {
      try {
        if (!frappe.session.user || frappe.session.user === "Guest") {
          return;
        }
        var full_name = frappe.boot.user.full_name || frappe.session.user;
        var names = full_name.trim().split(/\s+/);
        var display_name = "";
        if (names.length > 1) {
          display_name = names[0] + " " + names[names.length - 1].charAt(0).toUpperCase();
        } else {
          display_name = names[0];
        }
        var $userButton = $(".navbar .dropdown-navbar-user > .btn-reset.nav-link");
        if ($userButton.length === 0) {
          $userButton = $(".navbar .dropdown-navbar-user button").first();
          if ($userButton.length === 0) {
            return;
          }
        }
        $userButton.empty();
        var $nameSpan = $('<span class="user-name-display"></span>').text(display_name).css({
          "display": "inline-block",
          "padding": "8px 12px",
          "background": "var(--dark-green-avatar-bg)",
          "color": "var(--dark-green-avatar-color)",
          "border-radius": "4px",
          "font-size": "14px",
          "font-weight": "500",
          "white-space": "nowrap"
        });
        $userButton.append($nameSpan);
      } catch (e) {
      }
    }
  })();
})();
//# sourceMappingURL=whitelabel.bundle.TU7ZAZLG.js.map
