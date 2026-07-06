from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, OTPToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone_number", "full_name", "email", "is_staff", "is_active")
    search_fields = ("phone_number", "full_name", "email")
    list_filter = ("is_staff", "is_active")
    ordering = ("phone_number",)

    # layout for editing existing user
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal info", {"fields": ("full_name", "email", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # simple layout for creating a user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "full_name", "email", "password1", "password2"),
            },
        ),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "street_address", "is_default")
    list_filter = ("city", "is_default")
    search_fields = ("user__phone_number", "user__full_name", "city", "street_address")


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "otp_code", "created_at")
    search_fields = ("phone_number",)
    readonly_fields = ("created_at",)
