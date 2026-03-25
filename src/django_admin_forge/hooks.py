from collections.abc import Callable
from dataclasses import dataclass

from django.template.loader import render_to_string

from .conf import get_forge_settings

import time

_PROCESS_START = time.monotonic()


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


def _format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    minutes, s = divmod(seconds, 60)
    hours, m = divmod(minutes, 60)
    days, h = divmod(hours, 24)
    if days:
        return f"{days}d {h}h"
    if hours:
        return f"{hours}h {m}m"
    if minutes:
        return f"{minutes}m"
    return f"{s}s"


def _metric_uptime(_request, _spec: dict) -> dict:
    return {"label": "Uptime", "value": _format_duration(time.monotonic() - _PROCESS_START), "status": "ok"}


def _metric_django_version(_request, _spec: dict) -> dict:
    import django

    return {"label": "Django", "value": django.get_version(), "status": "ok"}


def _metric_debug(_request, _spec: dict) -> dict:
    from django.conf import settings

    enabled = bool(getattr(settings, "DEBUG", False))
    return {"label": "Debug", "value": "On" if enabled else "Off", "status": "warn" if enabled else "ok"}


def _metric_database(_request, _spec: dict) -> dict:
    from django.db import connections

    alias = str(_spec.get("alias") or "default")
    try:
        conn = connections[alias]
        conn.ensure_connection()
        engine = (conn.settings_dict.get("ENGINE") or "").rsplit(".", 1)[-1] or "db"
        return {"label": f"Database ({alias})", "value": engine, "status": "ok"}
    except Exception:
        return {"label": f"Database ({alias})", "value": "Unavailable", "status": "error"}


def _metric_cache(_request, _spec: dict) -> dict:
    from django.core.cache import caches

    alias = str(_spec.get("alias") or "default")
    try:
        cache = caches[alias]
        backend = cache.__class__.__module__.rsplit(".", 1)[-1] or "cache"
        # best-effort ping (won't error for locmem)
        cache.get("__forge_healthcheck__")
        return {"label": f"Cache ({alias})", "value": backend, "status": "ok"}
    except Exception:
        return {"label": f"Cache ({alias})", "value": "Unavailable", "status": "error"}


def _metric_celery(_request, _spec: dict) -> dict:
    """
    Optional integration: Celery.

    - If Celery isn't installed, we skip by raising ImportError in the handler setup.
    - If installed but not configured, we return a warning.
    - If configured, we best-effort ping workers with a short timeout.
    """
    from django.conf import settings

    try:
        from celery import current_app as celery_app
    except Exception:
        return {"label": "Celery", "value": "Not installed", "status": "warn"}

    broker_url = getattr(settings, "CELERY_BROKER_URL", None) or getattr(celery_app.conf, "broker_url", None)
    if not broker_url:
        return {"label": "Celery", "value": "Not configured", "status": "warn"}

    timeout = float(_spec.get("timeout", 1.0))
    try:
        insp = celery_app.control.inspect(timeout=timeout)
        replies = insp.ping() or {}
        if replies:
            return {"label": "Celery", "value": f"{len(replies)} worker(s) online", "status": "ok"}
        return {"label": "Celery", "value": "No workers responding", "status": "warn"}
    except Exception:
        return {"label": "Celery", "value": "Ping failed", "status": "error"}


def _metric_sentry(_request, _spec: dict) -> dict:
    """
    Optional integration: Sentry SDK.

    We don't attempt to fetch event counts (requires Sentry API access). This metric
    only surfaces whether Sentry appears enabled/configured in this process.
    """
    from django.conf import settings

    try:
        import sentry_sdk  # type: ignore
    except Exception:
        return {"label": "Sentry", "value": "Not installed", "status": "warn"}

    dsn = getattr(settings, "SENTRY_DSN", None)
    try:
        hub_dsn = getattr(getattr(getattr(sentry_sdk, "Hub", None), "current", None), "client", None)
        if hub_dsn and getattr(hub_dsn, "dsn", None):
            dsn = dsn or str(hub_dsn.dsn)
    except Exception:
        pass

    if dsn:
        return {"label": "Sentry", "value": "Enabled", "status": "ok"}
    return {"label": "Sentry", "value": "Installed (no DSN)", "status": "warn"}


DEFAULT_SYSTEM_HEALTH = [
    {"metric": "uptime"},
    {"metric": "django_version"},
    {"metric": "database"},
    {"metric": "cache"},
    {"metric": "debug"},
]


METRIC_HANDLERS = {
    "uptime": _metric_uptime,
    "django_version": _metric_django_version,
    "database": _metric_database,
    "cache": _metric_cache,
    "debug": _metric_debug,
    "celery": _metric_celery,
    "sentry": _metric_sentry,
}


def _system_health_context(request):
    forge_settings = get_forge_settings()
    configured = forge_settings.system_health_metrics or DEFAULT_SYSTEM_HEALTH

    items: list[dict] = []
    for spec in configured:
        metric = (spec.get("metric") or "").strip()
        handler = METRIC_HANDLERS.get(metric)
        if not handler:
            continue
        item = handler(request, spec)
        if spec.get("label"):
            item["label"] = str(spec["label"])
        items.append(item)

    severity = {"ok": 0, "warn": 1, "error": 2}
    worst = "ok"
    for item in items:
        status = item.get("status") or "ok"
        if severity.get(status, 0) > severity[worst]:
            worst = status

    status_label = {"ok": "Operational", "warn": "Attention", "error": "Degraded"}.get(worst, "Operational")
    reasons: list[dict] = []
    for item in items:
        status = item.get("status") or "ok"
        if status in {"warn", "error"}:
            reasons.append(
                {
                    "label": item.get("label", "Metric"),
                    "value": item.get("value", ""),
                    "status": status,
                }
            )
    return {
        "items": items,
        "overall_status": status_label,
        "overall_level": worst,
        "overall_reasons": reasons,
    }


registry.register_dashboard_card(
    DashboardCard(
        key="system-health",
        title="System Health",
        template_name="admin/forge/cards/system_health.html",
        context_factory=_system_health_context,
    )
)
