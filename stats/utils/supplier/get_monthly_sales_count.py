from datetime import datetime, timedelta

from django.db.models import Count, F
from django.db.models.functions import ExtractMonth
from order.models import OrderItem


def get_total_sales(user, month):
    sales_count = (
        OrderItem.objects.filter(
            product__supplier=user,
            order__created__month=month,
        )
        .distinct()
        .annotate(month=ExtractMonth(F("order__created")))
        .aggregate(total_count=Count("id"))
    )

    return sales_count["total_count"] if sales_count["total_count"] else 0


def calculate_percentage_difference(current_sales, previous_sales):
    if previous_sales != 0:
        percentage_difference = ((current_sales - previous_sales) / previous_sales) * 100
    else:
        percentage_difference = 0

    return percentage_difference


def get_monthly_sales_count(user):
    now = datetime.now()
    current_month = now.month
    previous_month = (now.replace(day=1) - timedelta(days=1)).month

    current_month_sales = get_total_sales(user, current_month)
    previous_month_sales = get_total_sales(user, previous_month)

    percentage_difference = calculate_percentage_difference(
        current_month_sales, previous_month_sales
    )

    return current_month_sales, percentage_difference
