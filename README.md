# django-forge

`django-forge` is a modern, customizable Django admin framework for serious SaaS and enterprise apps.

It keeps Django admin's reliability and model integration, while upgrading the UI/UX, theming, and developer customization surface.

## Highlights

- Django-first admin replacement (`AdminSite`-based)
- Branded login and modern dashboard
- Customizable sidebar menus and app/model navigation
- Dark, light, and system themes
- Accent color system
- Improved changelist, filters, bulk actions, and empty states
- Improved add/edit form layout

## Install

```bash
pip install django-forge
```

For local development in this repository:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Integration

### 1) Add apps

```python
INSTALLED_APPS = [
    "django_forge",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # your apps...
]
```

### 2) Use Forge admin URLs

```python
from django.urls import path
from django_forge.site import forge_admin_site

urlpatterns = [
    path("admin/", forge_admin_site.urls),
]
```

### 3) Configure `DJANGO_FORGE` (optional but recommended)

```python
DJANGO_FORGE = {
    "brand_name": "Forge Admin",
    "brand_logo_text": "FORGE",
    "brand_tagline": "Modern Django operations panel",
    "accent_color": "green",
    "default_theme": "system",  # "light" | "dark" | "system"
    "show_sidebar_search": True,
    "enable_command_bar": True,
}
```

## Configuration Reference

Use the `DJANGO_FORGE` setting dictionary.

- `brand_name` (`str`): Header brand name.
- `brand_logo_text` (`str`): Compact sidebar/logo text.
- `brand_tagline` (`str`): Login/subtitle branding.
- `accent_color` (`str`): Accent token used in key actions and highlights.
- `default_theme` (`"light" | "dark" | "system"`): Initial theme mode.
- `show_sidebar_search` (`bool`): Sidebar search input visibility.
- `enable_command_bar` (`bool`): Header search/command input visibility.
- `menu_icons` (`dict[str, str]`): Overrides for app/model icons.
- `menu_tabs` (`list[dict]`): Sidebar menu tabs (top and bottom areas).

## Accent Colors

Supported `accent_color` values:

`blue`, `green`, `amber`, `violet`, `emerald`, `teal`, `cyan`, `sky`, `indigo`, `purple`, `pink`, `rose`, `red`, `orange`, `yellow`, `lime`, `slate`, `gray`, `zinc`, `neutral`, `stone`

Example:

```python
DJANGO_FORGE = {
    "accent_color": "rose",
}
```

## Sidebar Menus (`menu_tabs`)

By default, only `Dashboard` is shown.

You can fully configure sidebar tabs:

```python
DJANGO_FORGE = {
    "menu_tabs": [
        {"label": "Dashboard", "url_name": "admin:index", "icon": "layout-grid"},
        {"label": "Applications", "url_name": "admin:forge-applications", "icon": "layers"},
        {"label": "Users", "url_name": "admin:auth_user_changelist", "icon": "user"},
        {"label": "Documentation", "url": "/docs/", "icon": "external-link"},
    ]
}
```

Each tab supports:

- `label` (required)
- `url_name` (reverse name) or `url` (direct URL)
- `icon` (optional, defaults to `layout-grid`)

## Menu Icon Overrides (`menu_icons`)

You can override app/model icons by key:

```python
DJANGO_FORGE = {
    "menu_icons": {
        "auth": "shield",                # app-level
        "auth.user": "user",             # model-level
        "auth.group": "users",
        "demo_app.customer": "building",
    }
}
```

Resolution order:
1. `app_label.model_name`
2. `model_name`
3. `app_label`
4. built-in defaults

## Demo Project (this repo)

```bash
python demo/manage.py migrate
python demo/manage.py createsuperuser
python demo/manage.py runserver
```

Open: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Status and Roadmap

Current implementation includes custom site templates, dashboard, apps page, collapsible sidebar, filters modal, improved forms/changelists, search helpers, and theme controls.

Planned next:

- Saved views/filters
- Dashboard widget API expansion
- Accessibility and keyboard navigation improvements
- Packaging/build pipeline polish for production release

