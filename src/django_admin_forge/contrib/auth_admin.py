"""
User admin with groups and permissions on the *add* screen (not only after save).

Use on your Forge (or default) admin site::

    from django.contrib.auth import get_user_model
    from django_admin_forge.contrib.auth_admin import ForgeUserAdmin
    from django_admin_forge.site import forge_admin_site

    forge_admin_site.register(get_user_model(), ForgeUserAdmin)

If you use a highly custom user model, subclass ``ForgeUserAdmin`` / forms as needed.
"""

from __future__ import annotations

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm
from django.utils.translation import gettext_lazy as _


class ForgeExtendedUserCreationForm(AdminUserCreationForm):
    """
    Same as Django's admin user creation form, plus status flags and M2M
    permission fields so they can be set before the first save.
    """

    class Meta(AdminUserCreationForm.Meta):
        fields = (
            "username",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and "is_active" in self.fields:
            self.fields["is_active"].initial = True
        perms = self.fields.get("user_permissions")
        if perms is not None:
            perms.queryset = perms.queryset.select_related("content_type")


class ForgeUserAdmin(UserAdmin):
    """
    ``UserAdmin`` with a richer add view: password, staff flags, groups, and
    user permissions in one step (Forge styling applies via ``change_form``).
    """

    add_form = ForgeExtendedUserCreationForm

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2"),
            },
        ),
        (
            _("Access"),
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
                "description": _(
                    "Staff may sign in to the admin. Superusers have all permissions "
                    "regardless of the choices below."
                ),
            },
        ),
        (
            _("Groups & permissions"),
            {
                "fields": ("groups", "user_permissions"),
            },
        ),
    )

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "user_permissions":
            qs = kwargs.get("queryset", db_field.remote_field.model.objects)
            kwargs["queryset"] = qs.select_related("content_type")
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)
