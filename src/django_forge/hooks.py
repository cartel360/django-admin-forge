from collections.abc import Callable
from dataclasses import dataclass


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


registry = HookRegistry()
