from django.contrib.admin import AdminSite
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import render
from django.urls import NoReverseMatch, path, reverse
from django.utils import timezone

from .conf import get_forge_settings
from .hooks import registry
from .icons import resolve_menu_icon
from .alerts import generate_needs_attention_alerts


class ForgeAdminSite(AdminSite):
    site_title = "Forge Admin"
    site_header = "Forge Admin"
    index_title = "Control Center"
    login_template = "admin/login.html"
    index_template = "admin/forge_dashboard.html"
    password_change_template = "admin/password_change_form.html"
    password_change_done_template = "admin/password_change_done.html"

    def _build_menu_tabs(self, menu_tabs: list[dict[str, str]]) -> list[dict[str, str]]:
        tabs = []
        for tab in menu_tabs:
            label = tab.get("label")
            if not label:
                continue
            url = tab.get("url")
            if not url:
                url_name = tab.get("url_name")
                if not url_name:
                    continue
                try:
                    url = reverse(url_name)
                except NoReverseMatch:
                    continue
            tabs.append(
                {
                    "label": label,
                    "icon": tab.get("icon", "layout-grid"),
                    "url": url,
                    "url_name": tab.get("url_name", ""),
                }
            )
        return tabs

    def _build_quick_links(self, links: list[dict[str, str]]) -> list[dict[str, str]]:
        resolved = []
        for link in links:
            label = link.get("label")
            if not label:
                continue
            url = link.get("url")
            if not url:
                url_name = link.get("url_name")
                if not url_name:
                    continue
                try:
                    url = reverse(url_name)
                except NoReverseMatch:
                    continue
            resolved.append(
                {
                    "label": str(label),
                    "url": url,
                    "url_name": link.get("url_name", ""),
                    "icon": link.get("icon", ""),
                }
            )
        return resolved

    def each_context(self, request):
        context = super().each_context(request)
        forge_settings = get_forge_settings()
        app_list = []
        for app in context.get("available_apps", []):
            app_label = (app.get("app_label") or "").lower()
            app_copy = {**app, "icon": resolve_menu_icon(forge_settings.menu_icons, app_label=app_label)}
            models = []
            for model in app.get("models", []):
                object_name = (model.get("object_name") or model.get("name") or "").lower()
                model_copy = {
                    **model,
                    "icon": resolve_menu_icon(
                        forge_settings.menu_icons,
                        app_label=app_label,
                        model_name=object_name,
                    ),
                }
                models.append(model_copy)
            app_copy["models"] = models
            app_list.append(app_copy)
        context.update(
            {
                "forge": {
                    **forge_settings.as_context(),
                    "dashboard_quick_links": self._build_quick_links(forge_settings.dashboard_quick_links),
                },
                "forge_site_header": forge_settings.brand_name,
                "available_apps": app_list,
                "forge_menu_tabs": self._build_menu_tabs(forge_settings.menu_tabs),
            }
        )
        context["forge_menu_tabs_top"] = [
            tab
            for tab in context["forge_menu_tabs"]
            if (tab.get("label", "").lower() != "applications" and tab.get("url_name") != "admin:forge-applications")
        ]
        context["forge_menu_tabs_bottom"] = [
            tab
            for tab in context["forge_menu_tabs"]
            if (tab.get("label", "").lower() == "applications" or tab.get("url_name") == "admin:forge-applications")
        ]
        search_index = []
        for tab in context["forge_menu_tabs"]:
            if tab.get("label") and tab.get("url"):
                search_index.append({"label": tab["label"], "url": tab["url"], "kind": "tab"})
        for app in app_list:
            app_url = app.get("app_url")
            if app.get("name") and app_url:
                search_index.append({"label": app["name"], "url": app_url, "kind": "app"})
            for model in app.get("models", []):
                if model.get("name") and model.get("admin_url"):
                    search_index.append(
                        {
                            "label": f"{app.get('name', '')} / {model['name']}",
                            "url": model["admin_url"],
                            "kind": "model",
                        }
                    )
        context["forge_search_index"] = search_index
        return context

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("", self.admin_view(self.dashboard_view), name="index"),
            path("dashboard/", self.admin_view(self.dashboard_view), name="forge-dashboard"),
            path("applications/", self.admin_view(self.applications_view), name="forge-applications"),
        ]
        return custom + urls

    def dashboard_view(self, request):
        forge_settings = get_forge_settings()
        User = get_user_model()
        now = timezone.now()
        user_count = User.objects.count()
        staff_count = User.objects.filter(is_staff=True).count()
        active_count = User.objects.filter(is_active=True).count()
        recent_users = User.objects.order_by("-date_joined")[:5]
        recent_actions_qs = LogEntry.objects.select_related("user", "content_type").order_by("-action_time")[:8]

        action_labels = {
            ADDITION: "Created",
            CHANGE: "Updated",
            DELETION: "Deleted",
        }

        recent_actions = []
        for entry in recent_actions_qs:
            recent_actions.append(
                {
                    "user": entry.user.get_username() if entry.user else "System",
                    "object_repr": entry.object_repr,
                    "content_type": str(entry.content_type) if entry.content_type else "Object",
                    "action_label": action_labels.get(entry.action_flag, "Action"),
                    "action_time": entry.action_time,
                }
            )

        default_stats = [
            {"label": "Total users", "value": user_count, "icon": "users", "hint": "All user accounts"},
            {"label": "Staff users", "value": staff_count, "icon": "shield", "hint": "Back-office operators"},
            {"label": "Active users", "value": active_count, "icon": "activity", "hint": "Enabled accounts"},
        ]
        custom_stats = []
        for card in forge_settings.dashboard_analytics_cards:
            if not card.get("label"):
                continue
            value = card.get("value")
            app_label = card.get("app_label")
            model_name = card.get("model")
            metric = card.get("metric", "count")
            queryset_filter = card.get("queryset_filter", {})
            if app_label and model_name:
                try:
                    model_cls = apps.get_model(str(app_label), str(model_name))
                    queryset = model_cls.objects.filter(**queryset_filter)
                    if metric == "count":
                        value = queryset.count()
                except Exception:
                    # Ignore invalid metric config and fall back to provided value.
                    if value is None:
                        value = "—"
            custom_stats.append(
                {
                    "label": str(card.get("label")),
                    "value": value if value is not None else "—",
                    "icon": card.get("icon", "activity"),
                    "hint": card.get("hint", ""),
                    "trend": card.get("trend", ""),
                }
            )
        dashboard_stats = custom_stats or default_stats

        # Optional: configurable “Recent records” card
        recent_records_card = None
        cfg = forge_settings.dashboard_recent_records or {}
        model_label = str(cfg.get("model") or "").strip()
        if model_label and "." in model_label:
            try:
                app_label, model_name = model_label.split(".", 1)
                model_cls = apps.get_model(app_label, model_name)
            except Exception:
                model_cls = None
            if model_cls is not None:
                try:
                    limit = int(cfg.get("limit", 5))
                except Exception:
                    limit = 5
                limit = max(1, min(limit, 10))

                title = str(cfg.get("title") or f"Recent {model_cls._meta.verbose_name_plural.title()}")
                icon = str(cfg.get("icon") or "clock")
                order_by = str(cfg.get("order_by") or "-pk")
                primary = str(cfg.get("primary_field") or "")
                secondary = str(cfg.get("secondary_field") or "")
                meta = str(cfg.get("meta_field") or "")

                try:
                    qs = model_cls.objects.all().order_by(order_by)[:limit]
                    rows = []
                    for obj in qs:
                        rows.append(
                            {
                                "pk": getattr(obj, "pk", None),
                                "primary": getattr(obj, primary) if primary else str(obj),
                                "secondary": getattr(obj, secondary) if secondary else "",
                                "meta": getattr(obj, meta) if meta else "",
                            }
                        )
                    changelist_url = ""
                    try:
                        changelist_url = reverse(
                            f"admin:{model_cls._meta.app_label}_{model_cls._meta.model_name}_changelist"
                        )
                    except NoReverseMatch:
                        changelist_url = ""
                    recent_records_card = {
                        "title": title,
                        "icon": icon,
                        "rows": rows,
                        "changelist_url": changelist_url,
                    }
                except Exception:
                    recent_records_card = None

        context = {
            **self.each_context(request),
            "title": "Dashboard",
            "now": now,
            "stats": dashboard_stats,
            "recent_users": recent_users,
            "recent_actions": recent_actions,
            "recent_records_card": recent_records_card,
        }
        recent_users_url = None
        for app in context.get("available_apps", []):
            for model in app.get("models", []):
                if model.get("object_name") == "User":
                    recent_users_url = model.get("admin_url")
                    break
            if recent_users_url:
                break
        context["recent_users_url"] = recent_users_url
        context["dashboard_cards"] = registry.get_rendered_dashboard_cards(request, context)
        # Rule-driven dashboard alerts (optional).
        raw_rules = forge_settings.needs_attention or forge_settings.dashboard_alert_rules
        generated_alerts = generate_needs_attention_alerts(request, raw_rules) if isinstance(raw_rules, dict) else []
        context["forge"] = {
            **(context.get("forge") or {}),
            "dashboard_alerts": generated_alerts,
        }
        return render(request, "admin/forge_dashboard.html", context)

    def applications_view(self, request):
        context = {
            **self.each_context(request),
            "title": "Applications",
        }
        return render(request, "admin/forge_applications.html", context)


forge_admin_site = ForgeAdminSite(name="forge_admin")
