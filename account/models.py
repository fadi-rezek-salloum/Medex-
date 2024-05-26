import uuid

from common.utils.file_upload_paths import (
    buyers_profile_pictures_path,
    suppliers_profile_pictures_path,
)
from common.validators.image_extension_validator import image_extension_validator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class Address(models.Model):
    country = models.CharField(_("Country"), max_length=50)
    state = models.CharField(_("State"), max_length=50, null=True, blank=True)
    city = models.CharField(_("City"), max_length=50, null=True, blank=True)

    postal_code = models.CharField(_("Postal Code"), max_length=15)

    address_1 = models.CharField(_("Address Line 1"), max_length=255)
    address_2 = models.CharField(_("Address Line 2"), max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.address_1}"


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    email = models.EmailField(_("Email"), max_length=255, unique=True)
    full_name = models.CharField(_("Full Name"), max_length=255)

    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_staff = models.BooleanField(_("Is Admin"), default=False)
    is_supplier = models.BooleanField(_("Is Supplier"), default=False)
    is_buyer = models.BooleanField(_("Is Buyer"), default=False)

    phone = models.CharField(_("Phone Number"), max_length=20)

    shipping_address = models.ForeignKey(
        Address,
        related_name="user_shipping",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Shipping Address"),
    )

    billing_address = models.ForeignKey(
        Address,
        related_name="user_billing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Billing Address"),
    )

    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    created = models.DateTimeField(_("Added On"), auto_now_add=True)
    updated = models.DateTimeField(_("Edited On"), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "phone"]

    def __str__(self):
        return self.email


class BuyerProfile(models.Model):
    user = models.OneToOneField(User, related_name="buyer_profile", on_delete=models.CASCADE)

    profile_picture = models.ImageField(
        _("Profile Picture"),
        upload_to=buyers_profile_pictures_path,
        validators=[image_extension_validator],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.full_name


class SupplierProfile(models.Model):
    user = models.OneToOneField(User, related_name="supplier_profile", on_delete=models.CASCADE)

    profile_picture = models.ImageField(
        _("Profile Picture"),
        upload_to=suppliers_profile_pictures_path,
        validators=[image_extension_validator],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.full_name
