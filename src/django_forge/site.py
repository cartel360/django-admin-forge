from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.shortcuts import render
from django.urls import path
from django.utils import timezone

from .conf import get_forge_settings
from .hooks import registry


class ForgeAdminSite(AdminSite):
    site_title = "Forge Admin"
    site_header = "Forge Admin"
    index_title = "Control Center"
    login_template = "admin/login.html"
    index_template = "admin/forge_dashboard.html"

    def each_context(self, request):
        context = super().each_context(request)
        forge_settings = get_forge_settings()
        context.update(
            {
                "forge": forge_settings.as_context(),
                "forge_site_header": forge_settings.brand_name,
            }
        )
        return context

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("", self.admin_view(self.dashboard_view), name="index"),
            path("dashboard/", self.admin_view(self.dashboard_view), name="forge-dashboard"),
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
                {"label": "Total users", "value": user_count},
                {"label": "Staff users", "value": staff_count},
                {"label": "Active users", "value": active_count},
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


forge_admin_site = ForgeAdminSite(name="forge_admin")
