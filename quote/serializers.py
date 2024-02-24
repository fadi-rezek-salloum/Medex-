from account.serializers import UserSerializer
from django.db.models import Q
from django.utils import timezone
from django.utils.timesince import timesince
from product.models import Product
from rest_framework import serializers

from .models import QuoteAttachment, QuoteOffer, QuoteRequest


class QuoteAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteAttachment
        fields = "__all__"


class QuoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(allow_null=True, required=False)
    attachments = serializers.SerializerMethodField()
    created_since = serializers.SerializerMethodField()
    unit_display = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    due_date_display = serializers.SerializerMethodField(read_only=True)
    due_time_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuoteRequest
        fields = "__all__"

    def get_attachments(self, obj):
        attachments = obj.quoteattachment_set.all()
        serializer = QuoteAttachmentSerializer(attachments, many=True)
        return serializer.data

    def get_created_since(self, obj):
        return timesince(obj.created, timezone.now())

    def get_unit_display(self, obj):
        return obj.get_unit_display()

    def get_product_name(self, obj):
        products = Product.objects.filter(
            Q(slug__icontains=obj.product) | Q(name__icontains=obj.product)
        ).first()

        try:
            if products:
                return products.name
            else:
                return obj.product
        except AttributeError:
            return obj.product

    def get_due_date_display(self, obj):
        return obj.due_date.date()

    def get_due_time_display(self, obj):
        due_time = obj.due_date.time()
        formatted_time = due_time.strftime("%I:%M %p")
        return formatted_time


class QuoteOfferSerializer(serializers.ModelSerializer):
    user = UserSerializer(allow_null=True, required=False)
    quote_obj = serializers.SerializerMethodField(read_only=True)
    created_since = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuoteOffer
        fields = "__all__"

    def get_created_since(self, obj):
        return timesince(obj.created, timezone.now())

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_quote_obj(self, obj):
        quote_obj = QuoteSerializer(obj.quote)

        return quote_obj.data
