from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from .site import forge_admin_site


@staff_member_required
def dashboard_view(request):
    User = get_user_model()
    now = timezone.now()
    user_count = User.objects.count()
    staff_count = User.objects.filter(is_staff=True).count()
    active_count = User.objects.filter(is_active=True).count()
    recent_users = User.objects.order_by("-date_joined")[:5]
    model_counts = ContentType.objects.values("app_label").annotate(total=Count("id")).order_by("-total")[:6]

    context = {
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
    context.update(forge_admin_site.each_context(request))
    return render(request, "admin/forge_dashboard.html", context)
