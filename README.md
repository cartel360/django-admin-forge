# django-forge

`django-forge` is a modern, extensible Django admin framework designed for production SaaS and enterprise applications.

## Goals

- Preserve Django admin's reliability and ecosystem.
- Deliver a premium UI/UX with a modern design system.
- Provide clean extension points for themes, components, and plugins.
- Stay server-rendered and Django-first, with progressive enhancement.

## Current Status

This repository contains:

- A reusable package scaffold in `src/django_forge/`.
- A demo Django project in `demo/` for local development.
- A first working MVP custom `AdminSite` with:
  - branded login
  - custom dashboard
  - modern sidebar layout
  - dark mode toggle
  - improved changelist and change form templates

## Quickstart (Demo)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python demo/manage.py migrate
python demo/manage.py createsuperuser
python demo/manage.py runserver
```

Open: <http://127.0.0.1:8000/admin/>

## Package Integration (Early API)

1. Add `django_forge` before `django.contrib.admin` in `INSTALLED_APPS`.
2. Use `django_forge.site.forge_admin_site.urls` for your admin URL.
3. Optionally configure `DJANGO_FORGE` in settings:

```python
DJANGO_FORGE = {
    "brand_name": "Forge Admin",
    "brand_logo_text": "FORGE",
    "accent_color": "blue",
    "default_theme": "system",  # "light" | "dark" | "system"
    "show_sidebar_search": True,
}
```

## Roadmap

- Pluggable dashboard cards/widgets
- Per-model layout customization hooks
- Reusable UI component library
- Enhanced filters/actions/search experiences
- Audit/activity views and analytics widgets
- Theme packs and organization branding

