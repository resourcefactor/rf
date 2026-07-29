# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this app is

`rf` is a Frappe framework app ("RF Whitelabel App") that whitelabels ERPNext/Frappe Desk and the public
website for Resource Factors' branding (logos, favicon, navbar colors/title, login page branding, splash
image, update-popup suppression), plus a couple of small admin utilities layered on top of core Frappe
doctypes (User Permission, Note). It is not a standalone app — it runs inside a Frappe bench alongside
other apps (ERPNext, etc.) and depends on the bench's Python/Node environment.

Bench: `~/frappe-bench15` (production-grade, v15). This app has no `package.json`/test suite of its own;
JS tooling and linting run from the bench root via `pre-commit`.

## Common commands

Run from the bench root (`~/frappe-bench15`), not from `apps/rf`, unless noted.

```bash
# Apply DocType/schema changes after editing any doctype .json
bench --site <site> migrate

# Run an arbitrary Python function in the app (e.g. one-off patches/utilities)
bench execute rf.api.<method_name>
bench execute rf.patches.patch_datatable_index_width.execute

# Restart to pick up hooks.py / server-side changes
bench restart

# Rebuild JS bundles (whitelabel.bundle.js etc.) after editing rf/public/js
bench build --app rf

# Watch mode during frontend development
bench watch

# Console for ad-hoc debugging
bench --site <site> console
```

Linting/formatting (from `apps/rf`, via pre-commit — there is no separate lint/test npm script):

```bash
pre-commit install       # one-time
pre-commit run --all-files
```

Pre-commit chain: `ruff` (import sort + lint + format, tab-indent/double-quote style per
`pyproject.toml`), `prettier` (js/vue/scss), `eslint` (js, `--quiet`). Excludes `rf/public/dist/**`,
`rf/templates/includes/**`, and `rf/public/js/lib/**` from prettier/eslint.

There is no automated test suite in this app currently (no `test_*.py` files beyond the Frappe
boilerplate `test_whitelabel_setting.py` stub). If you add tests, run them with:

```bash
bench --site <site> run-tests --app rf
```

## Architecture

### Whitelabeling flow (`rf/api.py`, `rf/hooks.py`)

This is the core of the app. Key hook wiring in `hooks.py`:

- `after_migrate = [whitelabel_patch, setup_note_company_field]` — re-applies branding and ensures the
  Note company-restriction custom field exists every time doctypes are migrated. `whitelabel_patch()`
  deletes the stock ERPNext welcome page, blanks the welcome blog post, and rewrites onboarding
  module/step titles and descriptions (replacing "ERPNext" with the configured `brand_name`), then
  updates Website Settings / System Settings (OTP issuer) app name.
- `boot_session` → `boot_session()` attaches the singleton `Whitelabel Setting` doc to `bootinfo` for
  logged-in users, which the client-side bundle (`whitelabel.bundle.js`) reads to apply navbar logo,
  colors, title, and to suppress the update popup.
- `extend_bootinfo` → `extend_bootinfo()` runs **after** `bootinfo.notes` is populated and filters login
  popup Notes by company: a Note's `restrict_to_companies` (child table `Note Restrict Company`, see
  `rf/custom/note.json` for the custom field fixture) is checked against the user's `User Permission`
  rows for `allow="Company"`; unrestricted notes still show to everyone. This must stay in
  `extend_bootinfo`, not `boot_session`, because notes aren't set yet at `boot_session` time.
- `update_website_context` → `get_website_context()` swaps in a custom login-page logo
  (`login_logo_url` from site config) but only for Guest sessions, so authenticated Desk sessions keep
  the navbar branding from `Whitelabel Setting`.
- `override_whitelisted_methods` replaces core `frappe.utils.change_log.show_update_popup` with
  `rf.api.ignore_update_popup`, which checks the `disable_new_update_popup` flag on `Whitelabel Setting`
  before showing the update popup.
- Branding/theming constants live in two places: `hooks.py` (`brand_html`, `brand_name`,
  `website_context` favicon/splash) for static/build-time values, and the singleton **Whitelabel
  Setting** doctype (`rf/rf/doctype/whitelabel_setting/`) for admin-editable values (logos, navbar
  colors/title, help menu visibility, update popup toggle).

### User Permission Manager (`rf/rf/page/user_permission_manager/`, `rf/api.py`)

A custom desk Page (not a DocType) that provides a bulk checkbox-grid UI for adding/removing
`User Permission` rows for a given user + `allow` doctype, instead of adding them one at a time via the
standard list. Access control is intentionally **not** hardcoded to System Manager — it mirrors
`Page.is_permitted()` via `check_user_permission_manager_access()` in `api.py`, so restricting/opening
access is done by editing the page's `roles` in `user_permission_manager.json`, not by changing Python.

- `get_user_permission_manager_data` — reads existing `for_value`s for a user/allow/scope tuple so the
  UI can pre-check the grid to match what's already saved. The filter tuple (`user`, `allow`,
  `applicable_for`, `apply_to_all_doctypes`) mirrors `User Permission`'s own duplicate-detection logic
  exactly, so the UI never disagrees with what the server considers a duplicate.
- `save_user_permission_manager_selection` — bulk create/delete. Each addition uses
  `frappe.db.savepoint()` per row and calls core `insert_user_perm()`; a row that fails validation
  (e.g. a duplicate "is default") is rolled back to its savepoint and skipped rather than aborting the
  whole batch — check the `skipped` list in the response rather than assuming success.

### Note company restriction (`rf/rf/doctype/note_restrict_company/`, `rf/custom/note.json`)

`Note Restrict Company` is a child table doctype attached to core `Note` via the `restrict_to_companies`
custom field (defined both as a fixture in `hooks.py` and defensively re-created by
`setup_note_company_field()` on every migrate, in case the fixture is missing on a given site). See the
whitelabeling flow section above for how this gates which login popups a user sees.

### Directory map

- `rf/api.py` — nearly all server-side whitelisted logic and hook targets for this app; start here.
- `rf/hooks.py` — all Frappe hook wiring; the source of truth for what runs when.
- `rf/rf/doctype/` — app-specific DocTypes (`Whitelabel Setting` singleton, `Note Restrict Company`
  child table).
- `rf/rf/page/` — custom Desk pages (`User Permission Manager`).
- `rf/custom/` — Frappe "customize form" fixtures applied to core doctypes (e.g. `note.json` adds the
  `restrict_to_companies` field to `Note`).
- `rf/patches/` — one-off data migration scripts invoked via `bench execute rf.patches.<module>.execute`
  (not wired into `patches.txt` — run manually per the README/hooks comments).
- `rf/public/js/whitelabel.bundle.js` — desk-side branding application (`app_include_js`).
- `rf/public/js/whitelabel_web.js` — public website branding application (`web_include_js`).
- `rf/templates/` — Jinja page templates for the public site.
- `rf/config/desktop.py`, `rf/config/docs.py` — standard Frappe app config stubs.

## Working conventions specific to this repo

- Formatting is tab-indented, double-quoted Python per `pyproject.toml`'s ruff config — let
  `ruff format` handle it rather than hand-matching style.
- Prefer `frappe.db.get_value/set_value`, `frappe.get_doc`, `frappe.qb` over raw SQL (one existing
  exception: `update_field_label()` in `api.py` uses raw SQL against `tabDocField` — don't treat that as
  a pattern to copy).
- New server-side entry points called from the client must be `@frappe.whitelist()`; guest-accessible
  endpoints (e.g. `get_login_logo_url`) additionally need `allow_guest=True`.
- When adding admin-editable branding options, add fields to the `Whitelabel Setting` singleton rather
  than introducing a new settings doctype.
