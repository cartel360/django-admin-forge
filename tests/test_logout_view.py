import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_admin_logout_renders_forge_logged_out_page():
    User = get_user_model()
    User.objects.create_user(username="staff", password="pw", is_staff=True)
    client = Client()
    assert client.login(username="staff", password="pw")
    resp = client.post(reverse("admin:logout"))
    assert resp.status_code == 200
    assert b"You are signed out" in resp.content
    assert b"Sign in again" in resp.content
