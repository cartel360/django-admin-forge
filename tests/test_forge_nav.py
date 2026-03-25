from django_admin_forge.templatetags.forge_icons import (
    forge_dashboard_path_active,
    forge_sidebar_tab_active,
)


def test_model_menu_tab_active_for_add_and_change():
    tab = {
        "url": "/admin/demo_app/customer/",
        "url_name": "admin:demo_app_customer_changelist",
    }
    assert forge_sidebar_tab_active("/admin/demo_app/customer/", tab)
    assert forge_sidebar_tab_active("/admin/demo_app/customer/add/", tab)
    assert forge_sidebar_tab_active("/admin/demo_app/customer/uuid/change/", tab)
    assert forge_sidebar_tab_active("/admin/demo_app/customer/12/delete/", tab)


def test_model_menu_tab_not_active_for_other_model():
    tab = {
        "url": "/admin/demo_app/customer/",
        "url_name": "admin:demo_app_customer_changelist",
    }
    assert not forge_sidebar_tab_active("/admin/demo_app/subscription/add/", tab)
    assert not forge_sidebar_tab_active("/admin/", tab)


def test_dashboard_tab_active_includes_dashboard_alias_path():
    tab = {"url": "/admin/", "url_name": "admin:index"}
    assert forge_sidebar_tab_active("/admin/", tab)
    assert forge_sidebar_tab_active("/admin/dashboard/", tab)
    assert not forge_sidebar_tab_active("/admin/demo_app/customer/add/", tab)


def test_forge_dashboard_path_active_filter():
    assert forge_dashboard_path_active("/admin/")
    assert forge_dashboard_path_active("/admin/dashboard/")
    assert not forge_dashboard_path_active("/admin/demo_app/customer/")
