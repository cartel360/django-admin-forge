from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth import get_user_model
from django.urls import path

from django_admin_forge.site import forge_admin_site

try:
    forge_admin_site.register(get_user_model(), admin.ModelAdmin)
except AlreadyRegistered:
    pass

urlpatterns = [path("admin/", forge_admin_site.urls)]
