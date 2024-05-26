from datetime import datetime, timedelta

from django.db.models import F, Sum
from django.db.models.functions import ExtractMonth
from order.models import Order


def get_total_sales(user, month):
    sales_price = (
        Order.objects.filter(
            products__product__supplier=user,
            created__month=month,
        )
        .distinct()
        .annotate(month=ExtractMonth(F("created")))
        .aggregate(total_money=Sum("products__total_price"))
    )

    return sales_price["total_money"] if sales_price["total_money"] else 0


def calculate_percentage_difference(current_sales, previous_sales):
    if previous_sales != 0:
        percentage_difference = ((current_sales - previous_sales) / previous_sales) * 100
    else:
        percentage_difference = 0

    return percentage_difference


def get_monthly_sales(user):
    now = datetime.now()
    current_month = now.month
    previous_month = (now.replace(day=1) - timedelta(days=1)).month

    current_month_sales = get_total_sales(user, current_month)
    previous_month_sales = get_total_sales(user, previous_month)

    percentage_difference = calculate_percentage_difference(
        current_month_sales, previous_month_sales
    )

    return current_month_sales, percentage_difference
