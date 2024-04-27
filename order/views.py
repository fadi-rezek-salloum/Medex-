import json

from account.serializers import AddressSerializer
from common.utils.generate_tracking_number import generate_tracking_number
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from product.models import Product
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from stats.utils.supplier.get_monthly_and_daily_sales import get_monthly_and_daily_sales
from stats.utils.supplier.get_monthly_and_daily_sales_count import (
    get_monthly_and_daily_sales_count,
)
from stats.utils.supplier.get_monthly_new_buyers import get_monthly_new_buyers
from stats.utils.supplier.get_monthly_sales import get_monthly_sales
from stats.utils.supplier.get_monthly_sales_count import get_monthly_sales_count
from stats.utils.supplier.get_monthly_threads_count import get_monthly_threads_count
from wallet.services import TransactionService

from .mixins import (
    CheckProductManagerGroupMixin,
    CheckSaleManagerGroupMixin,
    CheckSupplierSaleManagerGroupMixin,
)
from .models import Order, OrderItem, ReturnRequest
from .pagination import OrderItemPagination, ReturnRequestPagination
from .serializers import (
    OrderItemsSerializer,
    OrderSerializer,
    ReturnRequestFileSerializer,
    ReturnRequestSerializer,
)


class CheckoutView(CheckProductManagerGroupMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            user = request.user
            cartItems = json.loads(data["cartItems"])

            if data.get("sameAddress") == "true":
                if user.billing_address != user.shipping_address:
                    user.billing_address = user.shipping_address
                    user.save()
                else:
                    pass
            else:
                address = AddressSerializer(data=json.loads(data.get("billing_address")))
                address.is_valid(raise_exception=True)
                address = address.save()
                user.billing_address = address
                user.save()

            pm = "CASH" if data["cashPayment"] == "true" else ""

            order = Order.objects.create(user=user, payment_method=pm)

            for i in cartItems:
                quantity = i.pop("qty")

                product = Product.objects.get(sku=i.pop("sku"))

                product.stock_quantity = product.stock_quantity - quantity
                product.save()

                order_item = OrderItem.objects.create(
                    user=user, quantity=quantity, product=product
                )

                order.products.add(order_item)

            order.save()

            return Response(status=status.HTTP_200_OK)
        except Exception as ex:
            print(ex)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderItemListView(CheckSaleManagerGroupMixin, generics.ListAPIView):
    pagination_class = OrderItemPagination
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemsSerializer
    queryset = OrderItem.objects.all().order_by("-created")

    def get_queryset(self):
        qs = OrderItem.objects.all().order_by("-created")

        if self.request.user.is_supplier:
            qs = qs.filter(
                Q(product__supplier=self.request.user)
                | Q(product__supplier=self.request.user.parent)
            ).distinct()
        elif self.request.user.is_buyer:
            qs = qs.filter(
                Q(user=self.request.user) | Q(user=self.request.user.parent)
            ).distinct()

        return qs

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        stats = request.GET.get("stats", None)

        # Get the paginated data
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            response_data = {
                "results": serializer.data,
            }

            if stats:
                (
                    months,
                    days,
                    monthly_sales,
                    daily_sales,
                ) = get_monthly_and_daily_sales(request.user)

                daily_sales_counts = get_monthly_and_daily_sales_count(request.user)

                current_month_sales, percentage_difference = get_monthly_sales(request.user)
                (
                    current_month_sales_count,
                    count_percentage_difference,
                ) = get_monthly_sales_count(request.user)

                (
                    current_month_buyers,
                    buyers_percentage_difference,
                ) = get_monthly_new_buyers(request.user)

                (
                    current_month_threads,
                    threads_percentage_difference,
                ) = get_monthly_threads_count(request.user)

                response_data["stats"] = {
                    "monthly_sales": [months, monthly_sales],
                    "daily_sales": [days, daily_sales],
                    "daily_sales_counts": daily_sales_counts,
                    "current_monthly_sales": [current_month_sales, percentage_difference],
                    "monthly_sales_count": [
                        current_month_sales_count,
                        count_percentage_difference,
                    ],
                    "monthly_buyers_count": [
                        current_month_buyers,
                        buyers_percentage_difference,
                    ],
                    "monthly_threads_count": [
                        current_month_threads,
                        threads_percentage_difference,
                    ],
                }

            return self.get_paginated_response(response_data)

        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "results": serializer.data,
        }

        if stats:
            (months, days, monthly_sales, daily_sales) = get_monthly_and_daily_sales(
                request.user
            )

            daily_sales_counts = get_monthly_and_daily_sales_count(request.user)

            current_month_sales, percentage_difference = get_monthly_sales(request.user)
            current_month_sales_count, count_percentage_difference = get_monthly_sales_count(
                request.user
            )
            (
                current_month_buyers,
                buyers_percentage_difference,
            ) = get_monthly_new_buyers(request.user)

            (
                current_month_threads,
                threads_percentage_difference,
            ) = get_monthly_threads_count(request.user)

            response_data["stats"] = {
                "monthly_sales": [months, monthly_sales],
                "daily_sales": [days, daily_sales],
                "daily_sales_counts": daily_sales_counts,
                "current_month_sales": [current_month_sales, percentage_difference],
                "monthly_sales_count": [
                    current_month_sales_count,
                    count_percentage_difference,
                ],
                "monthly_buyers_count": [
                    current_month_buyers,
                    buyers_percentage_difference,
                ],
                "monthly_threads_count": [
                    current_month_threads,
                    threads_percentage_difference,
                ],
            }

        return Response(response_data)


class OrderItemDetailView(CheckSaleManagerGroupMixin, generics.RetrieveAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemsSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    lookup_field = "id"


class OrderItemShippingAdvanceView(CheckSupplierSaleManagerGroupMixin, generics.GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(OrderItem, id=request.data.get("id"))

        if request.user == order.product.supplier:
            if order.shipping_status == "OR":
                order.shipping_status = "P"
            elif order.shipping_status == "P":
                order.shipping_status = "OTW"
            else:
                order.shipping_status = "DE"

            order.save()

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderReturnView(CheckSaleManagerGroupMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReturnRequestSerializer
    queryset = ReturnRequest.objects.all()

    def get(self, request, *args, **kwargs):
        req = get_object_or_404(ReturnRequest, id=kwargs["id"])
        serializer_context = self.get_serializer_context()
        serializer = ReturnRequestSerializer(req, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs.get("id"))

        user = request.user

        # Check if a return request already exists for the user and product
        existing_return_request = ReturnRequest.objects.filter(
            user=user, product=order_item
        ).exists()
        if existing_return_request:
            return Response(
                {"error": "exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()

        data["tracking_number"] = generate_tracking_number()

        files = request.FILES.getlist("files[]")
        data.pop("files[]")
        data["status"] = "AP"

        return_serializer = ReturnRequestSerializer(data=data)
        return_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            return_instance = return_serializer.save(user=user, product=order_item)

            for f in files:
                file_data = {"evidence_file": f}
                file_serializer = ReturnRequestFileSerializer(data=file_data)
                file_serializer.is_valid(raise_exception=True)
                file_serializer.save(return_request=return_instance)

            TransactionService.create_transaction(
                user.id,
                user.wallet.id,
                order_item.total_price,
                "R",
                "P",
                return_order=return_instance,
            )

        return Response(status=status.HTTP_200_OK)


class OrderReturnListView(CheckSaleManagerGroupMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer
    pagination_class = ReturnRequestPagination

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_supplier:
            qs = qs.filter(product__product__supplier=self.request.user)
        elif self.request.user.is_buyer:
            qs = qs.filter(user=self.request.user)

        return qs


class OrderReturnApproveView(CheckSupplierSaleManagerGroupMixin, generics.GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        rr = get_object_or_404(ReturnRequest, id=kwargs["id"])

        if not rr.product.product.supplier == request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        rr.status = "APR"

        rr.save()

        transaction = TransactionService.retrieve_transaction_by_return_id(rr.id)

        TransactionService.approve_transaction(transaction.id)

        return Response(status=status.HTTP_200_OK)


class OrderReturnDeclineView(CheckSupplierSaleManagerGroupMixin, generics.GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        rr = get_object_or_404(ReturnRequest, id=kwargs["id"])

        if not rr.product.product.supplier == request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        rr.status = "DEC"
        rr.decline_reason = request.POST.get("reason")

        rr.save()

        transaction = TransactionService.retrieve_transaction_by_return_id(rr.id)

        TransactionService.decline_transaction(transaction.id)

        return Response(status=status.HTTP_200_OK)
