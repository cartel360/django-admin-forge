from dataclasses import asdict, dataclass, field

from django.conf import settings

ACCENT_HEX = {
    "blue": "#2563eb",
    "green": "#16a34a",
    "amber": "#d97706",
    "violet": "#7c3aed",
    "emerald": "#059669",
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

    def as_context(self) -> dict:
        data = asdict(self)
        data["accent_hex"] = ACCENT_HEX.get(self.accent_color, ACCENT_HEX["blue"])
        return data


def get_forge_settings() -> ForgeSettings:
    user_settings = getattr(settings, "DJANGO_FORGE", {})
    valid_keys = {field.name for field in ForgeSettings.__dataclass_fields__.values()}
    filtered = {key: value for key, value in user_settings.items() if key in valid_keys}
    return ForgeSettings(**filtered)
