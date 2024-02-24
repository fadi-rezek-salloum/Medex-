from datetime import datetime, timedelta

from account.serializers import UserSerializer
from product.serializers import ProductSerializer
from rest_framework import serializers

from .models import Order, OrderItem, ReturnRequest, ReturnRequestFile


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    user = UserSerializer()

    final_price = serializers.SerializerMethodField(read_only=True)
    is_returnable = serializers.SerializerMethodField(read_only=True)
    is_return_requested = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    decline_reason = serializers.SerializerMethodField(read_only=True)
    created_date = serializers.SerializerMethodField(read_only=True)
    created_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"
        ordering = ("-created",)

    def get_final_price(self, obj):
        if obj.product.sale_price > 0:
            return obj.get_total_discount_product_price()
        return obj.get_total_product_price()

    def get_created_date(self, obj):
        return obj.created.date()

    def get_created_time(self, obj):
        return obj.created.time()

    def get_is_returnable(self, obj):
        product = obj.product
        return_deadline = timedelta(days=product.return_deadline)
        order_created = obj.created.date()
        current_date = datetime.now().date()
        days_since_order = (current_date - order_created).days
        days_since_order_timedelta = timedelta(days=days_since_order)
        return days_since_order_timedelta <= return_deadline and product.is_returnable

    def get_is_return_requested(self, obj):
        return obj.returnrequest_set.exists()

    def get_status(self, obj):
        try:
            return obj.returnrequest_set.first().status
        except AttributeError:
            return None

    def get_shipping_status_display(self, obj):
        return obj.get_status_display()

    def get_decline_reason(self, obj):
        try:
            return obj.returnrequest_set.first().decline_reason
        except AttributeError:
            return None


class ReturnRequestFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequestFile
        fields = ("evidence_file",)


class ReturnRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    created_date = serializers.SerializerMethodField(read_only=True)
    is_delivered = serializers.SerializerMethodField(read_only=True)
    evidence_files = serializers.SerializerMethodField(read_only=True)
    product = OrderItemsSerializer(read_only=True)

    class Meta:
        model = ReturnRequest
        fields = "__all__"

    def get_created_date(self, obj):
        return obj.created.date()

    def get_is_delivered(self, obj):
        return obj.product.shipping_status == "DE"

    def get_evidence_files(self, obj):
        files = obj.returnrequestfile_set.all()
        serializer = ReturnRequestFileSerializer(files, many=True)
        return serializer.data
