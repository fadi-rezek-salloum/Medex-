from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Address, BuyerProfile, SupplierProfile

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = "__all__"


class SupplierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProfile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    shipping_address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), many=False, required=False, allow_null=True
    )
    billing_address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), many=False, required=False, allow_null=True
    )
    profile_picture = serializers.ImageField(required=False, allow_null=True, write_only=True)

    groups = serializers.SerializerMethodField(read_only=True)

    created_date = serializers.SerializerMethodField(read_only=True)
    created_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "password",
            "phone",
            "shipping_address",
            "billing_address",
            "profile_picture",
            "is_buyer",
            "is_supplier",
            "groups",
            "created_date",
            "created_time",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def get_created_date(self, obj):
        return obj.created.date()

    def get_created_time(self, obj):
        return obj.created.time()

    def get_groups(self, obj):
        group_mappings = {
            "Supplier Product Manager": "p_man",
            "Supplier Quote Manager": "q_man",
            "Supplier Sale Manager": "s_man",
            "Supplier Chat": "c_man",
            "Buyer Product Manager": "p_man",
            "Buyer Quote Manager": "q_man",
            "Buyer Order Manager": "o_man",
            "Buyer Chat": "c_man",
        }

        group_names = list(obj.groups.values_list("name", flat=True))
        group_shortcuts = [group_mappings.get(name) for name in group_names]

        return group_shortcuts

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        try:
            buyer_profile = instance.buyer_profile
            profile_serializer = BuyerProfileSerializer(instance=buyer_profile)
            representation["profile"] = profile_serializer.data
        except BuyerProfile.DoesNotExist:
            pass

        try:
            supplier_profile = instance.supplier_profile
            profile_serializer = SupplierProfileSerializer(instance=supplier_profile)
            representation["profile"] = profile_serializer.data
        except SupplierProfile.DoesNotExist:
            pass

        representation["shipping_address"] = AddressSerializer(
            instance=instance.shipping_address
        ).data
        representation["billing_address"] = AddressSerializer(
            instance=instance.billing_address
        ).data

        return representation


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["full_name"] = user.full_name
        token["group_names"] = list(user.groups.values_list("name", flat=True))

        if user.parent is not None:
            token["parent"] = str(user.parent.id)
            token["role"] = "supplier" if user.is_supplier else "buyer"
        else:
            token["parent"] = None
            token["role"] = (
                "admin" if user.is_staff else "supplier" if user.is_supplier else "buyer"
            )

        try:
            if user.is_supplier:
                token["profile_picture"] = user.supplier_profile.profile_picture.url
            else:
                token["profile_picture"] = user.buyer_profile.profile_picture.url
        except ValueError:
            token["profile_picture"] = None

        return token
