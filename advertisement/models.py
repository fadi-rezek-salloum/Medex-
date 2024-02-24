from common.utils.file_upload_paths import ads_thumbnail_images_path
from common.validators.image_extension_validator import image_extension_validator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Advertisement(models.Model):
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=ads_thumbnail_images_path,
        null=True,
        blank=True,
        validators=[image_extension_validator],
    )

    def __str__(self):
        return self.thumbnail.url
