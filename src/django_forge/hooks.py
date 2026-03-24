from collections.abc import Callable
from dataclasses import dataclass

from django.template.loader import render_to_string


@dataclass(frozen=True)
class DashboardCard:
    key: str
    title: str
    template_name: str
    context_factory: Callable


class HookRegistry:
    def __init__(self) -> None:
        self.dashboard_cards: list[DashboardCard] = []

    def register_dashboard_card(self, card: DashboardCard) -> None:
        self.dashboard_cards.append(card)

    def get_rendered_dashboard_cards(self, request, base_context: dict) -> list[dict]:
        rendered = []
        for card in self.dashboard_cards:
            context = {**base_context, **card.context_factory(request)}
            html = render_to_string(card.template_name, context=context, request=request)
            rendered.append({"key": card.key, "title": card.title, "html": html})
        return rendered


registry = HookRegistry()


def _system_health_context(_request):
    return {
        "items": [
            {"label": "Uptime", "value": "Healthy"},
            {"label": "Queue", "value": "Idle"},
            {"label": "Errors (24h)", "value": "0 critical"},
        ]
    }


registry.register_dashboard_card(
    DashboardCard(
        key="system-health",
        title="System Health",
        template_name="admin/forge/cards/system_health.html",
        context_factory=_system_health_context,
    )
)
