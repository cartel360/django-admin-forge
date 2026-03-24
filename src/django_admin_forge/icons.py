from collections.abc import Mapping

DEFAULT_APP_ICONS = {
    "auth": "shield",
    "admin": "layout-grid",
    "contenttypes": "layers",
    "sessions": "clock",
}

DEFAULT_MODEL_KEYWORD_ICONS = {
    "user": "user",
    "group": "users",
    "customer": "building",
    "team": "users",
    "invoice": "receipt",
    "payment": "credit-card",
    "plan": "sparkles",
    "order": "shopping-bag",
}

FALLBACK_APP_ICON = "folder"
FALLBACK_MODEL_ICON = "file"


def resolve_menu_icon(menu_icons: Mapping[str, str], app_label: str, model_name: str | None = None) -> str:
    app_label = (app_label or "").lower()
    model_name = (model_name or "").lower()

    if model_name:
        if f"{app_label}.{model_name}" in menu_icons:
            return menu_icons[f"{app_label}.{model_name}"]
        if model_name in menu_icons:
            return menu_icons[model_name]

    if app_label in menu_icons:
        return menu_icons[app_label]

    if model_name:
        for keyword, icon in DEFAULT_MODEL_KEYWORD_ICONS.items():
            if keyword in model_name:
                return icon
        return FALLBACK_MODEL_ICON

    return DEFAULT_APP_ICONS.get(app_label, FALLBACK_APP_ICON)
