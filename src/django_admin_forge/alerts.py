from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Literal, TypedDict
from urllib.parse import urlencode

from django.apps import apps
from django.contrib import admin
from django.db.models import Model, Q
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.module_loading import import_string


Level = Literal["info", "success", "warning", "danger"]
DisplayMode = Literal["grouped", "per_row", "hybrid"]


class AlertRow(TypedDict, total=False):
    label: str
    value: str
    url: str


class DashboardAlert(TypedDict, total=False):
    title: str
    description: str
    level: Level
    icon: str
    url: str
    cta: str
    count: int
    rows: list[AlertRow]
    rule_id: str


@dataclass(frozen=True)
class NeedsAttentionConfig:
    enabled: bool
    rules: list[dict[str, Any]]
    display_mode: DisplayMode
    max_rows: int
    date_window_days: int
    use_utc: bool


def _parse_needs_attention_config(raw: dict[str, Any] | None) -> NeedsAttentionConfig:
    raw = raw or {}
    enabled = bool(raw.get("enabled", True))
    rules = list(raw.get("rules") or [])
    display = raw.get("display") or {}
    defaults = raw.get("defaults") or {}

    mode = str(display.get("mode") or "grouped")
    if mode not in ("grouped", "per_row", "hybrid"):
        mode = "grouped"

    try:
        max_rows = int(display.get("max_rows", 5))
    except Exception:
        max_rows = 5
    max_rows = max(1, min(max_rows, 25))

    try:
        window = int(defaults.get("date_window_days", 14))
    except Exception:
        window = 14
    window = max(0, min(window, 3650))

    tz_mode = str(defaults.get("timezone") or "current")
    use_utc = tz_mode.lower() == "utc"

    return NeedsAttentionConfig(
        enabled=enabled,
        rules=rules,
        display_mode=mode,  # type: ignore[assignment]
        max_rows=max_rows,
        date_window_days=window,
        use_utc=use_utc,
    )


def _now(cfg: NeedsAttentionConfig) -> datetime:
    dt = timezone.now()
    if cfg.use_utc:
        return dt.astimezone(timezone.utc)
    return dt


def _model_from_label(label: str):
    if "." not in label:
        raise ValueError("Model must be in the form 'app_label.ModelName'")
    app_label, model_name = label.split(".", 1)
    model = apps.get_model(app_label, model_name)
    if model is None:
        raise ValueError(f"Unknown model '{label}'")
    return model


def _validate_field(model: type[Model], field_name: str):
    try:
        return model._meta.get_field(field_name)
    except Exception as e:
        raise ValueError(f"Unknown field '{field_name}' on {model._meta.label}") from e


def _admin_changelist_url(model: type[Model], filters: dict[str, str] | None = None) -> str:
    opts = model._meta
    url_name = f"admin:{opts.app_label}_{opts.model_name}_changelist"
    try:
        base = reverse(url_name)
    except NoReverseMatch:
        return ""
    if not filters:
        return base
    return f"{base}?{urlencode(filters)}"


def _admin_change_url(model: type[Model], pk: Any) -> str:
    opts = model._meta
    url_name = f"admin:{opts.app_label}_{opts.model_name}_change"
    try:
        return reverse(url_name, args=[pk])
    except NoReverseMatch:
        return ""


def _safe_str(value: Any) -> str:
    try:
        return str(value)
    except Exception:
        return "—"


def _coerce_date(value: datetime | date) -> date:
    return value.date() if isinstance(value, datetime) else value


def _build_date_due(rule: dict[str, Any], cfg: NeedsAttentionConfig, model: type[Model]) -> tuple[Q, dict[str, str], dict[str, str]]:
    field = str(rule.get("field") or "").strip()
    if not field:
        raise ValueError("date_due rule requires 'field'")
    f = _validate_field(model, field)
    if f.get_internal_type() not in {"DateField", "DateTimeField"}:
        raise ValueError("date_due rule field must be DateField or DateTimeField")

    direction = str(rule.get("direction") or "within_or_past")
    if direction not in {"within", "past", "within_or_past"}:
        direction = "within_or_past"

    include_null = bool(rule.get("include_null", False))
    try:
        window_days = int(rule.get("window_days", cfg.date_window_days))
    except Exception:
        window_days = cfg.date_window_days
    window_days = max(0, min(window_days, 3650))

    now_dt = _now(cfg)
    end_dt = now_dt + timedelta(days=window_days)

    if f.get_internal_type() == "DateField":
        now_val = _coerce_date(now_dt)
        end_val = _coerce_date(end_dt)
        filters: dict[str, str] = {}
        q = Q()
        if direction in {"past", "within_or_past"}:
            q |= Q(**{f"{field}__lt": now_val})
            filters[f"{field}__lt"] = now_val.isoformat()
        if direction in {"within", "within_or_past"}:
            q |= Q(**{f"{field}__range": (now_val, end_val)})
            filters[f"{field}__range"] = f"{now_val.isoformat()},{end_val.isoformat()}"
        if include_null:
            q |= Q(**{f"{field}__isnull": True})
            filters[f"{field}__isnull"] = "True"
        return q, filters, {"order_by": field}

    # DateTimeField
    now_val_dt = now_dt
    end_val_dt = end_dt
    filters_dt: dict[str, str] = {}
    q_dt = Q()
    if direction in {"past", "within_or_past"}:
        q_dt |= Q(**{f"{field}__lt": now_val_dt})
        filters_dt[f"{field}__lt"] = now_val_dt.isoformat()
    if direction in {"within", "within_or_past"}:
        q_dt |= Q(**{f"{field}__range": (now_val_dt, end_val_dt)})
        filters_dt[f"{field}__range"] = f"{now_val_dt.isoformat()},{end_val_dt.isoformat()}"
    if include_null:
        q_dt |= Q(**{f"{field}__isnull": True})
        filters_dt[f"{field}__isnull"] = "True"
    return q_dt, filters_dt, {"order_by": field}


def _build_numeric_threshold(rule: dict[str, Any], model: type[Model]) -> tuple[Q, dict[str, str], dict[str, str]]:
    field = str(rule.get("field") or "").strip()
    if not field:
        raise ValueError("numeric_threshold rule requires 'field'")
    _validate_field(model, field)

    op = str(rule.get("op") or "<").strip()
    if op not in {"<", "<=", ">", ">=", "=="}:
        op = "<"
    value = rule.get("value")
    if value is None:
        raise ValueError("numeric_threshold rule requires 'value'")

    include_null = bool(rule.get("include_null", False))
    lookup_map = {"<": "lt", "<=": "lte", ">": "gt", ">=": "gte", "==": "exact"}
    lookup = lookup_map[op]
    q = Q(**{f"{field}__{lookup}": value})
    filters = {f"{field}__{lookup}": _safe_str(value)}
    if include_null:
        q |= Q(**{f"{field}__isnull": True})
        filters[f"{field}__isnull"] = "True"
    return q, filters, {}


def _build_bool_flag(rule: dict[str, Any], model: type[Model]) -> tuple[Q, dict[str, str], dict[str, str]]:
    field = str(rule.get("field") or "").strip()
    if not field:
        raise ValueError("bool_flag rule requires 'field'")
    _validate_field(model, field)
    expected = rule.get("value", True)
    q = Q(**{field: bool(expected)})
    filters = {field: "True" if bool(expected) else "False"}
    return q, filters, {}


def _rule_level(rule: dict[str, Any]) -> Level:
    level = str(rule.get("level") or "warning").lower()
    return level if level in {"info", "success", "warning", "danger"} else "warning"  # type: ignore[return-value]


def _get_admin_site():
    # Support custom AdminSite instances; fall back to default.
    try:
        return admin.site
    except Exception:
        return None


def generate_needs_attention_alerts(request, raw_config: dict[str, Any] | None) -> list[DashboardAlert]:
    cfg = _parse_needs_attention_config(raw_config)
    if not cfg.enabled:
        return []

    alerts: list[DashboardAlert] = []
    for rule in cfg.rules:
        try:
            rule_id = str(rule.get("id") or "").strip()
            rule_type = str(rule.get("type") or "").strip()
            title = str(rule.get("title") or "").strip()
            if not rule_id or not rule_type or not title:
                continue

            icon = str(rule.get("icon") or "")
            cta = str(rule.get("cta") or "") or "View"
            mode = str(rule.get("display_mode") or cfg.display_mode)
            if mode not in ("grouped", "per_row", "hybrid"):
                mode = cfg.display_mode

            if rule_type == "callable":
                dotted = str(rule.get("callable") or "").strip()
                if not dotted:
                    continue
                fn = import_string(dotted)
                result = fn(request)
                if not result:
                    continue
                if isinstance(result, list):
                    for a in result:
                        if isinstance(a, dict):
                            alerts.append(a)  # type: ignore[arg-type]
                elif isinstance(result, dict):
                    alerts.append(result)  # type: ignore[arg-type]
                continue

            model_label = str(rule.get("model") or "").strip()
            if not model_label:
                continue
            model = _model_from_label(model_label)

            if rule_type == "date_due":
                q, filters, extra = _build_date_due(rule, cfg, model)
            elif rule_type == "numeric_threshold":
                q, filters, extra = _build_numeric_threshold(rule, model)
            elif rule_type == "bool_flag":
                q, filters, extra = _build_bool_flag(rule, model)
            else:
                continue

            qs = model.objects.filter(q)
            order_by = extra.get("order_by")
            if order_by:
                qs = qs.order_by(order_by)

            count = qs.only("pk").count()
            if count <= 0:
                continue

            url = str(rule.get("url") or "")
            if not url:
                url = _admin_changelist_url(model, filters)

            if mode == "grouped":
                description = str(rule.get("description") or "").strip()
                if not description:
                    description = f"{count} matching record(s)"
                alerts.append(
                    {
                        "rule_id": rule_id,
                        "title": title,
                        "description": description,
                        "level": _rule_level(rule),
                        "icon": icon,
                        "url": url,
                        "cta": cta,
                        "count": count,
                    }
                )
                continue

            # hybrid or per_row: fetch top N rows
            max_rows = int(rule.get("max_rows") or cfg.max_rows)
            max_rows = max(1, min(max_rows, 25))
            rows_qs = qs.only("pk")[:max_rows]
            rows: list[AlertRow] = []
            for obj in rows_qs:
                rows.append(
                    {
                        "label": _safe_str(obj),
                        "value": "",
                        "url": _admin_change_url(model, getattr(obj, "pk", None)),
                    }
                )

            if mode == "per_row":
                for r in rows:
                    alerts.append(
                        {
                            "rule_id": rule_id,
                            "title": r["label"],
                            "description": title,
                            "level": _rule_level(rule),
                            "icon": icon,
                            "url": r.get("url", "") or url,
                            "cta": cta,
                        }
                    )
                continue

            # hybrid
            description = str(rule.get("description") or "").strip()
            if not description:
                description = f"{count} matching record(s)"
            alerts.append(
                {
                    "rule_id": rule_id,
                    "title": title,
                    "description": description,
                    "level": _rule_level(rule),
                    "icon": icon,
                    "url": url,
                    "cta": cta,
                    "count": count,
                    "rows": rows,
                }
            )
        except Exception as e:
            alerts.append(
                {
                    "rule_id": str(rule.get("id") or ""),
                    "title": str(rule.get("title") or "Needs attention rule failed"),
                    "description": _safe_str(e),
                    "level": "danger",
                    "icon": "activity",
                    "url": "",
                    "cta": "",
                }
            )
    return alerts

