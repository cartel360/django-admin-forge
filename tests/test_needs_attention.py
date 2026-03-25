import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from django_admin_forge.alerts import generate_needs_attention_alerts


@pytest.mark.django_db
def test_needs_attention_bool_flag_generates_grouped_alert():
    User = get_user_model()
    User.objects.create_user(username="inactive", password="pass", is_active=False, is_staff=True)

    client = Client()
    config = {
        "display": {"mode": "grouped"},
        "rules": [
            {
                "id": "inactive-users",
                "type": "bool_flag",
                "title": "Inactive users",
                "model": "auth.User",
                "field": "is_active",
                "value": False,
                "level": "warning",
            }
        ],
    }
    alerts = generate_needs_attention_alerts(request=None, raw_config=config)  # type: ignore[arg-type]
    assert alerts
    assert alerts[0]["title"] == "Inactive users"
    assert alerts[0]["count"] >= 1


@pytest.mark.django_db
def test_needs_attention_date_due_on_datetime_field():
    User = get_user_model()
    u = User.objects.create_user(username="old", password="pass", is_staff=True, is_superuser=True)
    # force date_joined into the past so it's always < now
    User.objects.filter(pk=u.pk).update(date_joined=timezone.now() - timezone.timedelta(days=365))

    config = {
        "rules": [
            {
                "id": "joined-past",
                "type": "date_due",
                "title": "Old accounts",
                "model": "auth.User",
                "field": "date_joined",
                "direction": "past",
                "window_days": 1,
            }
        ]
    }
    alerts = generate_needs_attention_alerts(request=None, raw_config=config)  # type: ignore[arg-type]
    assert len(alerts) == 1
    assert alerts[0]["count"] >= 1
    assert "url" in alerts[0]


@pytest.mark.django_db
def test_dashboard_renders_needs_attention_section_when_configured(settings):
    settings.DJANGO_ADMIN_FORGE = {
        "needs_attention": {
            "rules": [
                {
                    "id": "inactive-users",
                    "type": "bool_flag",
                    "title": "Inactive users",
                    "model": "auth.User",
                    "field": "is_active",
                    "value": False,
                    "level": "warning",
                }
            ]
        }
    }
    User = get_user_model()
    User.objects.create_user(username="inactive", password="pass", is_active=False, is_staff=True)
    User.objects.create_user(username="staff", password="pass", is_staff=True, is_superuser=True)

    client = Client()
    assert client.login(username="staff", password="pass")
    resp = client.get(reverse("admin:index"))
    assert resp.status_code == 200
    assert b"Needs attention" in resp.content
