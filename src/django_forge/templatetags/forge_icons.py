import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ICON_PATHS = {
    "layout-grid": "M3 3h8v8H3V3zm10 0h8v5h-8V3zM3 13h5v8H3v-8zm7 3h11v5H10v-5z",
    "search": "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zm0 0 8 8",
    "user": "M20 21a8 8 0 1 0-16 0M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
    "users": "M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M16 3.13a4 4 0 0 1 0 7.75M23 21v-2a4 4 0 0 0-3-3.87",
    "shield": "M12 3l8 4v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V7l8-4z",
    "layers": "M12 2 2 7l10 5 10-5-10-5zm-10 9 10 5 10-5M2 15l10 5 10-5",
    "clock": "M12 8v5l3 3M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0z",
    "folder": "M3 6h6l2 2h10v10a2 2 0 0 1-2 2H3V6z",
    "file": "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z",
    "building": "M4 22h16M6 22V6h12v16M9 10h.01M9 14h.01M9 18h.01M15 10h.01M15 14h.01M15 18h.01",
    "receipt": "M6 2h12v20l-3-2-3 2-3-2-3 2V2z",
    "credit-card": "M2 7h20v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7zm0 0V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v2H2z",
    "sparkles": "M12 3l1.5 3.5L17 8l-3.5 1.5L12 13l-1.5-3.5L7 8l3.5-1.5L12 3zm7 9 1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2zM5 14l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z",
    "shopping-bag": "M6 8h12l1 13H5L6 8zm3 0V6a3 3 0 0 1 6 0v2",
    "activity": "M3 12h4l2-4 4 8 2-4h6",
    "sun": "M12 4V2M12 22v-2M4.93 4.93 6.34 6.34M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z",
    "moon": "M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z",
    "monitor": "M4 5h16v10H4V5zm4 14h8M10 15v4m4-4v4",
    "chevrons-up": "M17 11l-5-5-5 5M17 18l-5-5-5 5",
    "log-out": "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9",
    "key": "M21 2l-2 2m-7 7a5 5 0 1 1-7-7 5 5 0 0 1 7 7zm0 0 9-9 2 2-2 2 2 2-2 2-2-2-2 2-2-2z",
    "external-link": "M14 3h7v7M10 14 21 3M19 14v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h6",
}


@register.simple_tag
def forge_icon(name: str, extra_class: str = ""):
    path = ICON_PATHS.get(name, ICON_PATHS["file"])
    css = f"forge-icon {extra_class}".strip()
    svg = (
        f'<svg viewBox="0 0 24 24" aria-hidden="true" class="{css}" fill="none" '
        'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{path}"/></svg>'
    )
    return mark_safe(svg)


@register.filter
def forge_labelize(value):
    text = str(value or "")
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.title()
