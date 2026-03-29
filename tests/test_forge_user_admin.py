import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_user_add_form_includes_permissions_and_groups():
    User = get_user_model()
    User.objects.create_user(username="super", password="pw", is_staff=True, is_superuser=True)
    client = Client()
    assert client.login(username="super", password="pw")
    url = reverse("admin:auth_user_add")
    resp = client.get(url)
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "user_permissions" in body or "id_user_permissions" in body
    assert "groups" in body or "id_groups" in body
    assert "second step" in body.lower()
