# Django Admin Forge

Modern, customizable admin UI on top of Django’s admin: same models, permissions, and `ModelAdmin` patterns—upgraded layout, theming, dashboard, and navigation.

**Requirements:** Python 3.11+, Django 4.2–5.x (see `pyproject.toml`).

> **Developing the package or running the demo?** See [DEVELOPMENT.md](DEVELOPMENT.md).  
> **More detail:** [docs/](docs/) (architecture, configuration snippets, roadmap).

## Highlights

- Django-first `AdminSite` replacement (`forge_admin_site`)
- Branded login, dashboard, applications browser
- Sidebar search, header command/search, collapsible sidebar
- Light, dark, and system themes; configurable accent colors
- Improved changelist (filters modal, bulk actions, empty states) and change forms

## Install

From [PyPI](https://pypi.org/project/django-admin-forge/):

```bash
pip install django-admin-forge
```

If you previously used the `django-forge` distribution name: switch `INSTALLED_APPS` and imports to `django_admin_forge`, rename settings to `DJANGO_ADMIN_FORGE`, then `pip uninstall django-forge` if it was installed, and install this package instead.

## Quick integration

### 1. Add the app

`django_admin_forge` should be listed **before** `django.contrib.admin` so its admin templates take effect.

```python
INSTALLED_APPS = [
    "django_admin_forge",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # your apps...
]
```

### 2. Mount the Forge admin site

```python
from django.urls import path
from django_admin_forge.site import forge_admin_site

urlpatterns = [
    path("admin/", forge_admin_site.urls),
]
```

### 3. Optional: `DJANGO_ADMIN_FORGE`

```python
DJANGO_ADMIN_FORGE = {
    "brand_name": "Forge Admin",
    "brand_logo_text": "FORGE",
    "brand_tagline": "Modern Django operations panel",
    "accent_color": "green",
    "default_theme": "system",  # "light" | "dark" | "system"
    "show_sidebar_search": True,
    "enable_command_bar": True,
}
```

Run `collectstatic` in production like any Django app with packaged static files.

## Configuration reference

Use the `DJANGO_ADMIN_FORGE` dictionary in Django settings.

| Key | Description |
|-----|-------------|
| `brand_name` | Header / site title branding |
| `brand_logo_text` | Compact sidebar logo text |
| `brand_tagline` | Login and subtitle text |
| `accent_color` | Theme accent token (buttons, highlights) |
| `default_theme` | `"light"`, `"dark"`, or `"system"` |
| `show_sidebar_search` | Show sidebar search |
| `enable_command_bar` | Show header search / command input |
| `menu_icons` | Dict of icon overrides (see below) |
| `menu_tabs` | Sidebar tab entries (see below) |
| `dashboard_analytics_cards` | KPI cards backed by your models (see below) |
| `dashboard_quick_links` | Quick links shown on the dashboard (see below) |

## Accent colors

Supported `accent_color` values:

`blue`, `green`, `amber`, `violet`, `emerald`, `teal`, `cyan`, `sky`, `indigo`, `purple`, `pink`, `rose`, `red`, `orange`, `yellow`, `lime`, `slate`, `gray`, `zinc`, `neutral`, `stone`

```python
DJANGO_ADMIN_FORGE = {
    "accent_color": "rose",
}
```

## Sidebar tabs (`menu_tabs`)

Default: Dashboard only. Add entries with `url_name` (Django URL name) or `url` (path).

```python
DJANGO_ADMIN_FORGE = {
    "menu_tabs": [
        {"label": "Dashboard", "url_name": "admin:index", "icon": "layout-grid"},
        {"label": "Applications", "url_name": "admin:forge-applications", "icon": "layers"},
        {"label": "Users", "url_name": "admin:auth_user_changelist", "icon": "user"},
        {"label": "Docs", "url": "/docs/", "icon": "external-link"},
    ]
}
```

- `label` (required)
- `url_name` or `url`
- `icon` (optional; default `layout-grid`)

## Menu icon overrides (`menu_icons`)

Resolution order: `app_label.model_name`, then `model_name`, then `app_label`, then built-in defaults (see `django_admin_forge.icons`).

```python
DJANGO_ADMIN_FORGE = {
    "menu_icons": {
        "auth": "shield",
        "auth.user": "user",
        "auth.group": "users",
        "myapp.mymodel": "building",
    }
}
```

## Dashboard analytics cards

Configure KPI tiles with real data from your models (`metric`: `count` today; optional `queryset_filter`).

```python
DJANGO_ADMIN_FORGE = {
    "dashboard_analytics_cards": [
        {
            "label": "Orders",
            "app_label": "orders",
            "model": "Order",
            "metric": "count",
            "icon": "inbox",
            "hint": "All orders",
        },
        {
            "label": "Open orders",
            "app_label": "orders",
            "model": "Order",
            "metric": "count",
            "queryset_filter": {"status": "open"},
            "icon": "activity",
            "hint": "status = open",
        },
    ]
}
```

Fields: `label`, `app_label`, `model`, `metric`, optional `queryset_filter`, `value`, `icon`, `hint` / `trend`.

## Dashboard quick links

Add a “Quick links” section right after the KPI cards on the dashboard.

Each entry supports:

- `label` (required)
- `url_name` (Django URL name) **or** `url` (path/URL) (required)
- `icon` (optional)

```python
DJANGO_ADMIN_FORGE = {
    "dashboard_quick_links": [
        {"label": "Applications", "url_name": "admin:forge-applications", "icon": "layers"},
        {"label": "Users", "url_name": "admin:auth_user_changelist", "icon": "user"},
        {"label": "Docs", "url": "/docs/", "icon": "external-link"},
    ]
}
```

## License

MIT. See [LICENSE](LICENSE).
