from django.urls import path

from django_forge.site import forge_admin_site

urlpatterns = [path("admin/", forge_admin_site.urls)]
