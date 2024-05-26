from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .mixins import CheckBuyerAdminGroupMixin, CheckSupplierAdminGroupMixin
from .utils.buyer.get_categories_purchases import get_categories_purchases
from .utils.buyer.get_monthly_return_requests import get_monthly_return_requests
from .utils.buyer.get_monthly_rfq import get_monthly_rfq
from .utils.buyer.get_yearly_payments_per_month import get_yearly_payments_per_month
from .utils.buyer.get_yearly_purchases_per_month import get_yearly_purchases_per_month
from .utils.supplier.get_monthly_new_buyers import get_monthly_new_buyers
from .utils.supplier.get_monthly_quotes_statistics import get_monthly_quotes_statistics
from .utils.supplier.get_monthly_sales_count import get_monthly_sales_count
from .utils.supplier.get_monthly_sales_statistics import calculate_order_statistics
from .utils.supplier.get_products_statistics import (
    get_products_per_category,
    get_total_products_count,
)
from .utils.supplier.get_top_buyers_statistics import get_top_buyers_statistics


class BuyerStatsView(CheckBuyerAdminGroupMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        pass

    def get_serializer_class(self):
        pass

    def get(self, request, *args, **kwargs):
        months, yearly_payments_per_month = get_yearly_payments_per_month(request.user)
        yearly_purchases_per_month = get_yearly_purchases_per_month(request.user)
        monthly_return_requests = get_monthly_return_requests(request.user)
        monthly_rfq = get_monthly_rfq(request.user)
        categories, total_purchases = get_categories_purchases(request.user)

        response_data = {
            "yearly_payments": [months, yearly_payments_per_month],
            "yearly_purchases": [months, yearly_purchases_per_month],
            "monthly_return_requests": monthly_return_requests,
            "monthly_rfq": monthly_rfq,
            "categories_purchases": [categories, total_purchases],
        }

        return Response(response_data, status=status.HTTP_200_OK)


class SupplierStatsView(CheckSupplierAdminGroupMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        pass

    def get_serializer_class(self):
        pass

    def get(self, request, *args, **kwargs):
        monthly_sales_count, monthly_sales_count_percentage = get_monthly_sales_count(
            request.user
        )

        (
            monthly_orders_statistics,
            monthly_orders_statistics_percentage,
        ) = calculate_order_statistics(request.user)

        monthly_quotes_statistics = get_monthly_quotes_statistics(request.user)

        monthly_customers_count, monthly_customers_count_percentage = get_monthly_new_buyers(
            request.user
        )

        total_products_count = get_total_products_count(request.user)
        categories, products_counts = get_products_per_category(request.user)

        top_buyers_statistics = get_top_buyers_statistics(request.user)

        response_data = {
            "monthly_sales_count": monthly_sales_count,
            "monthly_sales_count_percentage": monthly_sales_count_percentage,
            "monthly_orders_statistics": monthly_orders_statistics,
            "monthly_orders_statistics_percentage": monthly_orders_statistics_percentage,
            "monthly_quotes_statistics": monthly_quotes_statistics,
            "monthly_customers_count": monthly_customers_count,
            "monthly_customers_count_percentage": monthly_customers_count_percentage,
            "total_products_count": total_products_count,
            "categories": categories,
            "products_counts": products_counts,
            "top_buyers_statistics": top_buyers_statistics,
        }

        return Response(response_data, status=status.HTTP_200_OK)
