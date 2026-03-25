import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from django_admin_forge.site import forge_admin_site


def _admin_request(rf):
    request = rf.get("/admin/")
    request.user = AnonymousUser()
    return request


@pytest.mark.django_db
def test_sidebar_injects_dashboard_and_applications_when_menu_tabs_empty(settings, rf):
    settings.DJANGO_ADMIN_FORGE = {"menu_tabs": []}
    ctx = forge_admin_site.each_context(_admin_request(rf))

    assert "forge" in ctx and ctx["forge"].get("brand_logo_src")
    assert "logo.png" in ctx["forge"]["brand_logo_src"]


@pytest.mark.django_db
def test_brand_logo_src_respects_override(settings, rf):
    settings.DJANGO_ADMIN_FORGE = {
        "menu_tabs": [],
        "brand_logo": "https://example.test/logo.svg",
    }
    ctx = forge_admin_site.each_context(_admin_request(rf))
    assert ctx["forge"]["brand_logo_src"] == "https://example.test/logo.svg"
    assert ctx["forge_menu_tabs_top"][0]["url_name"] == "admin:index"
    assert ctx["forge_menu_tabs_top"][0]["label"] == "Dashboard"
    assert len(ctx["forge_menu_tabs_bottom"]) == 1
    assert ctx["forge_menu_tabs_bottom"][0]["url_name"] == "admin:forge-applications"
    assert ctx["forge_menu_tabs"] == ctx["forge_menu_tabs_top"] + ctx["forge_menu_tabs_bottom"]


@pytest.mark.django_db
def test_sidebar_extra_tabs_follow_dashboard(settings, rf):
    settings.DJANGO_ADMIN_FORGE = {
        "menu_tabs": [
            {"label": "Users", "url_name": "admin:auth_user_changelist", "icon": "user"},
        ]
    }
    ctx = forge_admin_site.each_context(_admin_request(rf))

    assert len(ctx["forge_menu_tabs_top"]) == 2
    assert ctx["forge_menu_tabs_top"][0]["url_name"] == "admin:index"
    assert ctx["forge_menu_tabs_top"][1]["url_name"] == "admin:auth_user_changelist"
    assert ctx["forge_menu_tabs_top"][1]["url"] == reverse("admin:auth_user_changelist")
