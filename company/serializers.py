from account.models import Address
from account.serializers import AddressSerializer
from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), many=False)

    class Meta:
        model = Company
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["address"] = AddressSerializer(instance=instance.address).data

        return representation
