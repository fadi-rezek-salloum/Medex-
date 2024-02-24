from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from product.models import Product

User = get_user_model()


class Wishlist(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Wish List Items"

    def __str__(self):
        return f"{self.user.full_name} -> {self.product.name}"
