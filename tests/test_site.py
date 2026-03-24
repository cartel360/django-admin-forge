import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_admin_login_page_loads():
    client = Client()
    response = client.get(reverse("admin:login"))
    assert response.status_code == 200
    assert b"Forge" in response.content or b"forge" in response.content


@pytest.mark.django_db
def test_dashboard_requires_auth():
    client = Client()
    response = client.get(reverse("admin:index"))
    assert response.status_code in (302, 301)


@pytest.mark.django_db
def test_dashboard_loads_for_staff_user():
    User = get_user_model()
    user = User.objects.create_user(username="staff", password="pass", is_staff=True, is_superuser=True)
    client = Client()
    assert client.login(username="staff", password="pass")
    response = client.get(reverse("admin:index"))
    assert response.status_code == 200
    assert b"Dashboard" in response.content


@pytest.mark.django_db
def test_applications_page_loads_for_staff_user():
    User = get_user_model()
    User.objects.create_user(username="staff", password="pass", is_staff=True, is_superuser=True)
    client = Client()
    assert client.login(username="staff", password="pass")
    response = client.get(reverse("admin:forge-applications"))
    assert response.status_code == 200
    assert b"Applications" in response.content


@pytest.mark.django_db
def test_changelist_contains_required_actions_hooks():
    User = get_user_model()
    User.objects.create_user(username="staff", password="pass", is_staff=True, is_superuser=True)
    User.objects.create_user(username="row", password="pass", is_staff=True)
    client = Client()
    assert client.login(username="staff", password="pass")
    response = client.get(reverse("admin:auth_user_changelist"))
    assert response.status_code == 200
    assert b'id="changelist-form"' in response.content
    assert b'id="action-toggle"' in response.content
    assert b"action-counter" in response.content


@pytest.mark.django_db
def test_search_index_payload_is_rendered():
    User = get_user_model()
    User.objects.create_user(username="staff", password="pass", is_staff=True, is_superuser=True)
    client = Client()
    assert client.login(username="staff", password="pass")
    response = client.get(reverse("admin:index"))
    assert response.status_code == 200
    assert b'forge-search-index' in response.content
    assert b"Dashboard" in response.content
