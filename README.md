### RF

RF Whitelabel App for Frappe

## Logo Specifications

| Logo Type | Dimensions | File Format | Notes |
|-----------|------------|-------------|-------|
| **Navbar Logo** | 200px × 30-40px | SVG (recommended), PNG, JPG | Horizontal/wide format for navigation bar |
| **Login Page Logo** | 400px × 100px | SVG (recommended), PNG, JPG | Displayed on the login screen |
| **Splash Page Logo** | 512px × 512px | SVG (recommended), PNG | Square format for loading screen |
| **Favicon** | 32×32px or 192×192px | ICO, PNG | Browser tab icon |

**Tips:**
- Use **SVG** format when possible for crisp display at any resolution
- For PNG/JPG, use **2x dimensions** for retina displays (e.g., 400×80px for navbar logo)
- Keep file sizes under **100KB** for faster loading
- Use **transparent backgrounds** for logos (PNG or SVG)

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app rf
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/rf
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
