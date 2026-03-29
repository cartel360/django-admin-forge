from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group, User

from django_admin_forge.contrib.auth_admin import ForgeUserAdmin
from django_admin_forge.site import forge_admin_site

from .models import ApiKey, Customer, Invoice, Subscription


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_email", "plan", "seats", "is_active", "created_at")
    list_filter = ("plan", "is_active")
    search_fields = ("company_name", "contact_email")
    readonly_fields = ("created_at",)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("customer", "plan", "status", "expires_at", "auto_renew", "created_at")
    list_filter = ("plan", "status", "auto_renew")
    search_fields = ("customer__company_name",)
    readonly_fields = ("created_at",)


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner_email", "is_active", "expires_at", "last_used_at", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "owner_email")
    readonly_fields = ("created_at",)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "amount_cents", "due_date", "paid", "created_at")
    list_filter = ("paid",)
    search_fields = ("invoice_number", "customer__company_name")
    readonly_fields = ("created_at",)


forge_admin_site.register(Customer, CustomerAdmin)
forge_admin_site.register(Subscription, SubscriptionAdmin)
forge_admin_site.register(ApiKey, ApiKeyAdmin)
forge_admin_site.register(Invoice, InvoiceAdmin)
forge_admin_site.register(User, ForgeUserAdmin)
forge_admin_site.register(Group, GroupAdmin)
