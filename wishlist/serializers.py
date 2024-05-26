from product.serializers import ProductSerializer
from rest_framework import serializers

from .models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Wishlist
        fields = ("product",)
