from dataclasses import asdict, dataclass, field

from django.conf import settings

ACCENT_HEX = {
    "blue": "#2563eb",
    "green": "#16a34a",
    "amber": "#d97706",
    "violet": "#7c3aed",
    "emerald": "#059669",
    "teal": "#0d9488",
    "cyan": "#0891b2",
    "sky": "#0284c7",
    "indigo": "#4f46e5",
    "purple": "#9333ea",
    "pink": "#db2777",
    "rose": "#e11d48",
    "red": "#dc2626",
    "orange": "#ea580c",
    "yellow": "#ca8a04",
    "lime": "#65a30d",
    "slate": "#334155",
    "gray": "#4b5563",
    "zinc": "#52525b",
    "neutral": "#525252",
    "stone": "#57534e",
}


def _default_menu_tabs() -> list[dict[str, str]]:
    return [
        {
            "label": "Dashboard",
            "url_name": "admin:index",
            "icon": "layout-grid",
        }
    ]


@dataclass(frozen=True)
class ForgeSettings:
    brand_name: str = "Forge Admin"
    brand_logo_text: str = "FORGE"
    brand_tagline: str = "Modern Django operations panel"
    accent_color: str = "blue"
    default_theme: str = "system"  # light | dark | system
    show_sidebar_search: bool = True
    enable_command_bar: bool = True
    menu_icons: dict[str, str] = field(default_factory=dict)
    menu_tabs: list[dict[str, str]] = field(default_factory=_default_menu_tabs)
    dashboard_analytics_cards: list[dict] = field(default_factory=list)
    dashboard_quick_links: list[dict[str, str]] = field(default_factory=list)

    def as_context(self) -> dict:
        data = asdict(self)
        accent_name = (self.accent_color or "blue").lower()
        data["accent_hex"] = ACCENT_HEX.get(accent_name, ACCENT_HEX["blue"])
        data["accent_color"] = accent_name
        return data


def get_forge_settings() -> ForgeSettings:
    user_settings = getattr(settings, "DJANGO_ADMIN_FORGE", {})
    valid_keys = {field.name for field in ForgeSettings.__dataclass_fields__.values()}
    filtered = {key: value for key, value in user_settings.items() if key in valid_keys}
    return ForgeSettings(**filtered)
