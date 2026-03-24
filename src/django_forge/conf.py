from dataclasses import asdict, dataclass

from django.conf import settings


@dataclass(frozen=True)
class ForgeSettings:
    brand_name: str = "Forge Admin"
    brand_logo_text: str = "FORGE"
    brand_tagline: str = "Modern Django operations panel"
    accent_color: str = "blue"
    default_theme: str = "system"  # light | dark | system
    show_sidebar_search: bool = True
    enable_command_bar: bool = True

    def as_context(self) -> dict:
        return asdict(self)


def get_forge_settings() -> ForgeSettings:
    user_settings = getattr(settings, "DJANGO_FORGE", {})
    valid_keys = {field.name for field in ForgeSettings.__dataclass_fields__.values()}
    filtered = {key: value for key, value in user_settings.items() if key in valid_keys}
    return ForgeSettings(**filtered)
