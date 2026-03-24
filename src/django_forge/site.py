from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.shortcuts import render
from django.urls import NoReverseMatch, path, reverse
from django.utils import timezone

from .conf import get_forge_settings
from .hooks import registry
from .icons import resolve_menu_icon


class ForgeAdminSite(AdminSite):
    site_title = "Forge Admin"
    site_header = "Forge Admin"
    index_title = "Control Center"
    login_template = "admin/login.html"
    index_template = "admin/forge_dashboard.html"

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
                "forge": forge_settings.as_context(),
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
        User = get_user_model()
        now = timezone.now()
        user_count = User.objects.count()
        staff_count = User.objects.filter(is_staff=True).count()
        active_count = User.objects.filter(is_active=True).count()
        recent_users = User.objects.order_by("-date_joined")[:5]
        model_counts = ContentType.objects.values("app_label").annotate(total=Count("id")).order_by("-total")[:6]

        context = {
            **self.each_context(request),
            "title": "Dashboard",
            "now": now,
            "stats": [
                {"label": "Total users", "value": user_count, "icon": "users"},
                {"label": "Staff users", "value": staff_count, "icon": "shield"},
                {"label": "Active users", "value": active_count, "icon": "activity"},
            ],
            "recent_users": recent_users,
            "model_counts": model_counts,
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
        return render(request, "admin/forge_dashboard.html", context)

    def applications_view(self, request):
        context = {
            **self.each_context(request),
            "title": "Applications",
        }
        return render(request, "admin/forge_applications.html", context)


forge_admin_site = ForgeAdminSite(name="forge_admin")
