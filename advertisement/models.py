from common.utils.file_upload_paths import ads_thumbnail_images_path
from common.validators.image_extension_validator import image_extension_validator
from django.db import models
from django.utils.translation import gettext_lazy as _
from product.models import Category


class Advertisement(models.Model):
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=ads_thumbnail_images_path,
        null=True,
        blank=True,
        validators=[image_extension_validator],
    )

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True, default=None
    )

    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.thumbnail.url

    def save(self, *args, **kwargs):
        if not self.category:
            default_category, _ = Category.objects.get_or_create(name="generic")
            self.category = default_category
        super().save(*args, **kwargs)
