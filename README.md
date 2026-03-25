# Django Admin Forge

Modern, customizable admin UI on top of Django’s admin: same models, permissions, and `ModelAdmin` patterns—upgraded layout, theming, dashboard, and navigation.

**Requirements:** Python 3.11+, Django 4.2–5.x (see `pyproject.toml`).

> **Developing the package or running the demo?** See [DEVELOPMENT.md](DEVELOPMENT.md).  
> **More detail:** [docs/](docs/) (architecture, configuration snippets, roadmap).

## Highlights

- Django-first `AdminSite` replacement (`forge_admin_site`)
- Branded login, logout confirmation, dashboard, applications browser
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
    # Optional: "https://…", "/media/logo.png", or STATIC_URL path
    # "brand_logo": "/static/my-company/logo.svg",
    "brand_tagline": "Modern Django operations panel",
    "accent_color": "green",
    "default_theme": "system",  # "light" | "dark" | "system"
    "show_sidebar_search": True,
    "enable_command_bar": True,
}
```

Run `collectstatic` in production like any Django app with packaged static files.

Signing out shows a Forge-styled confirmation page (unless you set Django’s **`LOGOUT_REDIRECT_URL`**, which skips that screen and redirects immediately).

## Configuration reference

Use the `DJANGO_ADMIN_FORGE` dictionary in Django settings.

| Key | Description |
|-----|-------------|
| `brand_name` | Header / site title branding |
| `brand_logo_text` | Compact sidebar logo text |
| `brand_logo` | Optional image URL or path for the brand mark (sidebar + login). When unset, the bundled Django Admin Forge logo is used |
| `brand_tagline` | Login and subtitle text |
| `accent_color` | Theme accent token (buttons, highlights) |
| `default_theme` | `"light"`, `"dark"`, or `"system"` |
| `show_sidebar_search` | Show sidebar search |
| `enable_command_bar` | Show header search / command input |
| `menu_icons` | Dict of icon overrides (see below) |
| `menu_tabs` | Optional extra sidebar shortcuts (see below); Dashboard and Applications are always shown |
| `dashboard_analytics_cards` | KPI cards backed by your models (see below) |
| `dashboard_quick_links` | Quick links shown on the dashboard (see below) |
| `dashboard_recent_records` | Configurable “Recent records” dashboard card (see below) |
| `system_health_metrics` | System health metrics shown on the dashboard (see below) |
| `needs_attention` | Rule-driven “Needs attention” alerts (recommended; see below) |

## Accent colors

Supported `accent_color` values:

`blue`, `green`, `amber`, `violet`, `emerald`, `teal`, `cyan`, `sky`, `indigo`, `purple`, `pink`, `rose`, `red`, `orange`, `yellow`, `lime`, `slate`, `gray`, `zinc`, `neutral`, `stone`

```python
DJANGO_ADMIN_FORGE = {
    "accent_color": "rose",
}
```

## Sidebar tabs (`menu_tabs`)

**Dashboard** (`admin:index`) and **Applications** (`admin:forge-applications`) are always added for you: first item in the main nav and last item in the section above the account menu. You do not need to list them in settings.

Use `menu_tabs` only for **additional** shortcuts (with `url_name` as a Django URL name or `url` as a path). They appear after Dashboard in the order you define.

```python
DJANGO_ADMIN_FORGE = {
    "menu_tabs": [
        {"label": "Users", "url_name": "admin:auth_user_changelist", "icon": "user"},
        {"label": "Docs", "url": "/docs/", "icon": "external-link"},
    ]
}
```

If you still include Dashboard or Applications in `menu_tabs`, Forge uses your **label** and **icon** for those entries but keeps Dashboard first and Applications in the bottom group.

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

## Dashboard “Recent records” card

Replace the “Model groups” panel on the dashboard with a configurable “Recent records” card sourced from any model.

Config keys:

- `title` (optional)
- `model` (required): `"app_label.ModelName"`
- `icon` (optional)
- `limit` (optional, default 5; max 10)
- `order_by` (optional, default `-pk`)
- `primary_field` (optional; falls back to `str(obj)`)
- `secondary_field` (optional)
- `meta_field` (optional)

Example:

```python
DJANGO_ADMIN_FORGE = {
    "dashboard_recent_records": {
        "title": "Recent customers",
        "model": "demo_app.Customer",
        "icon": "building",
        "limit": 5,
        "order_by": "-created_at",
        "primary_field": "company_name",
        "secondary_field": "contact_email",
        "meta_field": "plan",
    },
}
```

## System health metrics

The “System health” dashboard card supports a configurable list of metrics. If you don’t configure anything, Forge shows a sensible default set based on Django itself (no Celery/Sentry/etc. required).

Supported built-in metrics:

- `uptime`
- `django_version`
- `database` (optional `alias`, default `"default"`)
- `cache` (optional `alias`, default `"default"`)
- `debug`
- `celery` (optional; requires Celery; optional `timeout`, default `1.0`)
- `sentry` (optional; requires `sentry-sdk`)

```python
DJANGO_ADMIN_FORGE = {
    "system_health_metrics": [
        {"metric": "uptime"},
        {"metric": "django_version"},
        {"metric": "database", "alias": "default"},
        {"metric": "cache", "alias": "default"},
        {"metric": "debug"},
        # Optional integrations (safe to include; will show "Not installed" if missing)
        {"metric": "celery", "timeout": 1.0},
        {"metric": "sentry"},
    ]
}
```

## Rule-driven “Needs attention” alerts

For most projects, you don’t want to hand-author every alert. Use `needs_attention` to generate alerts from **model data** (expiring subscriptions, stuck records, low quotas, etc.) with a small, robust config.

Top-level keys:

- `enabled` (default `True`)
- `rules`: list of rule dicts
- `display`: `{ "mode": "grouped"|"per_row"|"hybrid", "max_rows": 5 }`
- `defaults`: `{ "timezone": "current"|"utc", "date_window_days": 14 }`

Supported rule types:

- `date_due` (DateField/DateTimeField): within / overdue / both
- `numeric_threshold`
- `bool_flag`
- `callable` (escape hatch): dotted path returning alert dict(s)

Example:

```python
DJANGO_ADMIN_FORGE = {
    "needs_attention": {
        "display": {"mode": "hybrid", "max_rows": 5},
        "defaults": {"date_window_days": 14},
        "rules": [
            {
                "id": "customers-inactive",
                "type": "bool_flag",
                "title": "Inactive customers",
                "model": "demo_app.Customer",
                "field": "is_active",
                "value": False,
                "level": "warning",
                "icon": "building",
                "cta": "Review",
            },
            {
                "id": "low-seats",
                "type": "numeric_threshold",
                "title": "Large customers to review",
                "model": "demo_app.Customer",
                "field": "seats",
                "op": \">=\",
                "value": 50,
                "level": "info",
                "icon": "users",
            },
            {
                "id": "subscription-expiry",
                "type": "date_due",
                "title": "Subscriptions expiring soon",
                "model": "billing.Subscription",
                "field": "subscription_expiry",
                "window_days": 14,
                "direction": "within_or_past",
                "level": "danger",
                "icon": "clock",
            },
            {
                "id": "custom-check",
                "type": "callable",
                "title": "Custom checks",
                "callable": "myapp.admin_alerts.custom_alerts",
            },
        ],
    }
}
```

## License

MIT. See [LICENSE](LICENSE).
