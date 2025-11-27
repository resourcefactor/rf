# RF - Whitelabel App for Frappe/ERPNext v16

Comprehensive whitelabeling solution for Frappe/ERPNext version 16 beta.

## Features

- ✅ Hide help menu dropdown  
- ✅ Replace "ERPNext" → "ERP" in workspace titles
- ✅ Customize user display (FirstName L format with green background)
- ✅ Disable "What's New" update popups
- ✅ Custom navbar title and background color
- ✅ Email footer customization
- ✅ Brand logo and favicon support
- ✅ Compatible with v16 Espresso sidebar

## ⚠️ IMPORTANT: Clean Installation Required

**If you previously installed this app or see "frappe.ready is not a function" error:**

See [INSTALL.md](INSTALL.md) for detailed clean installation instructions.

Quick fix:
```bash
bench --site SITE uninstall-app rf
bench clear-cache
rm -rf assets/rf/ sites/assets/rf/
bench --site SITE install-app rf
bench build --app rf --force
bench restart
```

## Fresh Installation

```bash
bench get-app https://github.com/resourcefactor/rf.git --branch version-16
bench --site YOUR_SITE install-app rf
bench build --app rf
bench restart
```

## Configuration

Go to: **Setup > Whitelabel Setting**

Configure:
- General Settings (help menu, update popups, onboarding)
- Navbar Customization (title, background color)
- User Display (format selection)
- Email Settings (custom footer)
- Branding (app name, brand name)

## Logo Customization

**Method 1**: Setup > Navbar Settings > Application Logo

**Method 2**: Replace files:
- `rf/public/images/whitelabel_logo.svg` (32x32px)
- `rf/public/images/whitelabel_logo_long.svg` (150x32px)

## License

MIT
