from common.utils.create_slug import create_slug
from common.utils.file_upload_paths import (
    brands_images_path,
    categories_images_path,
    product_images_path,
)
from common.utils.generate_sku import generate_sku
from common.validators.image_extension_validator import image_extension_validator
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()


class Category(MPTTModel):
    name = models.CharField(_("Category Name"), max_length=255, unique=True)
    image = models.ImageField(
        _("Category Image"),
        upload_to=categories_images_path,
        validators=[image_extension_validator],
        default="uploads/images/placeholder/placeholder.png",
    )
    slug = models.SlugField(unique=True, null=True, blank=True)
    parent = TreeForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="children"
    )
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = create_slug(self.name)
        super().save(*args, **kwargs)

    @property
    def parent_name(self):
        if self.parent:
            return self.parent.name
        return None


class Brand(models.Model):
    name = models.CharField(_("Brand Name"), max_length=255, unique=True)
    image = models.ImageField(
        _("Brand Image"),
        upload_to=brands_images_path,
        validators=[image_extension_validator],
        default="uploads/images/placeholder/placeholder.png",
    )
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = create_slug(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    sku = models.CharField(primary_key=True, max_length=255, unique=True, blank=True)
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Supplier"))
    name = models.CharField(_("Product Name"), max_length=255)
    description = models.TextField(_("Description"))
    slug = models.SlugField(unique=True, null=True, blank=True)
    price = models.DecimalField(
        _("Price"), max_digits=10, decimal_places=2, null=True, blank=True
    )
    sale_price = models.DecimalField(
        _("Sale Price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.0,
    )
    price_range_min = models.DecimalField(
        _("Price Range - Min"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.0,
    )
    price_range_max = models.DecimalField(
        _("Price Range - Max"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.0,
    )
    category = TreeForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Category"),
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Brand")
    )
    stock_quantity = models.IntegerField(_("Stock Quantity"), default=0)
    is_available = models.BooleanField(_("Is Available ?"), default=True)
    is_returnable = models.BooleanField(_("Is Returnable ?"), default=False)
    return_deadline = models.IntegerField(_("Maximum Days To Return"), default=30)
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=product_images_path,
        null=True,
        blank=True,
        validators=[image_extension_validator],
    )
    image1 = models.ImageField(
        _("Image 1"),
        upload_to=product_images_path,
        blank=True,
        null=True,
        validators=[image_extension_validator],
    )
    image2 = models.ImageField(
        _("Image 2"),
        upload_to=product_images_path,
        blank=True,
        null=True,
        validators=[image_extension_validator],
    )
    image3 = models.ImageField(
        _("Image 3"),
        upload_to=product_images_path,
        blank=True,
        null=True,
        validators=[image_extension_validator],
    )
    image4 = models.ImageField(
        _("Image 4"),
        upload_to=product_images_path,
        blank=True,
        null=True,
        validators=[image_extension_validator],
    )
    created = models.DateTimeField(_("Added On"), auto_now_add=True)
    updated = models.DateTimeField(_("Edited On"), auto_now=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = generate_sku(self)
        if not self.slug:
            self.slug = create_slug(self.sku)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PrivateCategory(models.Model):
    name = models.CharField(_("Private Category Name"), max_length=100)
    supplier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Private Category Supplier"),
        null=True,
        blank=True,
    )
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return self.name
