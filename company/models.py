from account.models import Address, User
from common.utils.file_upload_paths import (
    company_cover_picture_path,
    company_profile_picture_path,
)
from common.validators.image_extension_validator import image_extension_validator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    supplier = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Company's Owner"),
    )

    name = models.CharField(_("Company Name"), max_length=255)
    email = models.EmailField(_("Company's Email address"))
    phone = models.CharField(_("Company's Phone Number"), max_length=20)

    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

    website = models.URLField(_("Company's Website"), null=True, blank=True)

    bio = models.TextField(_("Company's Bio"), null=True, blank=True)

    company_profile_picture = models.ImageField(
        _("Profile Picture"),
        upload_to=company_profile_picture_path,
        validators=[image_extension_validator],
        null=True,
        blank=True,
    )

    company_cover_picture = models.ImageField(
        _("Cover Picture"),
        upload_to=company_cover_picture_path,
        validators=[image_extension_validator],
        null=True,
        blank=True,
    )

    created = models.DateField(_("Company Created On"), default=timezone.now)
    updated = models.DateTimeField(_("Edited On"), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"
