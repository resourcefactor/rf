# Installation Instructions - IMPORTANT

## Problem: "frappe.ready is not a function" Error

If you see this error, it means old cached build files are being loaded.

## Solution: Clean Installation

```bash
# 1. Uninstall the app completely
bench --site YOUR_SITE_NAME uninstall-app rf

# 2. Clear ALL caches
bench clear-cache
bench clear-website-cache

# 3. Remove old build artifacts (IMPORTANT!)
rm -rf assets/rf/
rm -rf sites/assets/rf/
rm -rf sites/*/public/files/rf*

# 4. Reinstall the app
bench --site YOUR_SITE_NAME install-app rf

# 5. Force rebuild assets
bench build --app rf --force

# 6. Restart bench
bench restart

# 7. Clear browser cache
# Press Ctrl+Shift+R (or Cmd+Shift+R on Mac) to hard refresh
```

## Verify Installation

After following the steps above, check the browser console. You should see:
```
[RF Whitelabel] Whitelabel script loaded
[RF Whitelabel] Frappe object found, initializing...
[RF Whitelabel] DOM ready
```

## If Still Not Working

1. Check that only `whitelabel.bundle.js` exists:
   ```bash
   ls -la apps/rf/rf/public/js/
   # Should only show: whitelabel.bundle.js
   ```

2. Verify hooks.py is correct:
   ```bash
   grep "app_include_js" apps/rf/rf/hooks.py
   # Should show: app_include_js = "whitelabel.bundle.js"
   ```

3. Check browser Network tab:
   - Look for `whitelabel.bundle.js` being loaded
   - Should NOT see `rf.js` being loaded

4. If you still see `rf.js` in browser console:
   - There's a cached build somewhere
   - Run: `bench build --app rf --force --hard-link`
   - Restart: `bench restart`
   - Clear browser cache again

## Why This Happens

Frappe's build system caches JavaScript files. When you had a previous version of the app installed, it created `rf.js` in the build folder. That cached file persists even after uninstalling, causing the `frappe.ready is not a function` error (because `frappe.ready()` doesn't exist in Frappe v16).

The clean installation steps above ensure all old cached files are removed before reinstalling.
