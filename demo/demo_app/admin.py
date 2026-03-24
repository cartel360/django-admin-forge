from django.contrib import admin
from django.contrib.auth.models import Group, User

from django_admin_forge.site import forge_admin_site

from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_email", "plan", "seats", "is_active", "created_at")
    list_filter = ("plan", "is_active")
    search_fields = ("company_name", "contact_email")
    readonly_fields = ("created_at",)


forge_admin_site.register(Customer, CustomerAdmin)
forge_admin_site.register(User)
forge_admin_site.register(Group)
