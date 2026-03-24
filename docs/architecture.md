# Architecture

`django-forge` keeps Django admin internals while replacing presentation and adding extension hooks.

Core layers:

1. `site.py`: custom `ForgeAdminSite`.
2. `conf.py`: strongly typed package settings.
3. `views.py`: dashboard and future custom admin views.
4. `templates/admin/*`: UI overrides for login, dashboard, changelist, and forms.
5. `static/django_forge/*`: package CSS/JS assets.

Extension model:

- Add custom dashboard cards via registry/hooks (next milestone).
- Override templates at project level (`templates/admin/...`).
- Configure branding/theme through `DJANGO_FORGE`.
