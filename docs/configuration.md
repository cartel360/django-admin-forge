# Configuration

Use `DJANGO_ADMIN_FORGE` in Django settings.

```python
DJANGO_ADMIN_FORGE = {
    "brand_name": "Forge Admin",
    "brand_logo_text": "FORGE",
    # Optional image URL/path; default is the bundled Django Admin Forge logo.
    # "brand_logo": "/static/site/logo.png",
    "brand_tagline": "Modern Django operations panel",
    "accent_color": "blue",
    "default_theme": "system",
    "show_sidebar_search": True,
    "enable_command_bar": True,
}
```

`accent_color` supports:
`blue`, `green`, `amber`, `violet`, `emerald`, `teal`, `cyan`, `sky`, `indigo`, `purple`, `pink`, `rose`, `red`, `orange`, `yellow`, `lime`, `slate`, `gray`, `zinc`, `neutral`, `stone`.
