from account.serializers import AddressSerializer, UserSerializer
from django.utils import timezone
from django.utils.timesince import timesince
from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Opportunity


class OpportunitySerializer(TaggitSerializer, serializers.ModelSerializer):
    user = UserSerializer(allow_null=True, required=False)

    tags = TagListSerializerField()

    payment_method_display = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    value_display = serializers.SerializerMethodField(read_only=True)

    created_since = serializers.SerializerMethodField()
    delivery_date_display = serializers.SerializerMethodField(read_only=True)
    delivery_time_display = serializers.SerializerMethodField(read_only=True)

    suppliers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Opportunity
        exclude = ["target_suppliers", "payment_method", "status", "opportunity_value"]

    def get_payment_method_display(self, obj):
        return obj.get_payment_method_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_value_display(self, obj):
        return obj.get_opportunity_value_display()

    def get_created_since(self, obj):
        return timesince(obj.created, timezone.now())

    def get_delivery_date_display(self, obj):
        return obj.delivery_date.date()

    def get_delivery_time_display(self, obj):
        delivery_time = obj.delivery_date.time()
        formatted_time = delivery_time.strftime("%I:%M %p")
        return formatted_time

    def get_suppliers(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if user.is_authenticated:
            if obj.user == user:
                return UserSerializer(obj.target_suppliers, many=True).data
        else:
            return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["delivery_address"] = AddressSerializer(instance.delivery_address).data
        return representation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
