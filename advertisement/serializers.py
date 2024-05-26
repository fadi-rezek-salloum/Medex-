from product.serializers import CategorySerializer
from rest_framework import serializers

from .models import Advertisement


class AdvertisementSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Advertisement
        fields = "__all__"
