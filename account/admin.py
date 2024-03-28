from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin, TabularInline

from .models import Address, BuyerProfile, SupplierProfile, User

admin.site.register(Address)


class BuyerProfileInline(TabularInline):
    model = BuyerProfile
    fields = ["profile_picture"]
    extra = 1


class SupplierProfileInline(TabularInline):
    model = SupplierProfile
    fields = ["profile_picture"]
    extra = 1


@admin.register(User)
class CustomUserAdmin(ModelAdmin, BaseUserAdmin):
    inlines = [BuyerProfileInline, SupplierProfileInline]

    def get_inline_instances(self, request, obj=None):
        if obj and obj.is_buyer:
            return [BuyerProfileInline(self.model, self.admin_site)]
        elif obj and obj.is_supplier:
            return [SupplierProfileInline(self.model, self.admin_site)]
        return []

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("full_name", "phone")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_superuser", "is_staff", "is_supplier", "is_buyer")},
        ),
        ("Important dates", {"fields": ("last_login",)}),
        ("Addresses", {"fields": ("shipping_address", "billing_address")}),
        ("Groups and Permissions", {"fields": ("groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    list_display = ("email", "full_name", "is_active", "is_supplier", "is_buyer")
    list_filter = ("is_active", "is_supplier", "is_buyer")
    search_fields = ("email", "full_name")
    ordering = ("email",)
