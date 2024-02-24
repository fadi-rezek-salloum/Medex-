from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()


def get_new_buyer_count(supplier, month):
    new_buyer_count = (
        User.objects.filter(
            orders__products__product__supplier=supplier,
            orders__created__month=month,
            # orders__is_paid=True,
        )
        .distinct()
        .aggregate(total_count=Count("id"))
    )

    return new_buyer_count["total_count"] if new_buyer_count["total_count"] else 0


def calculate_percentage_difference(current_count, previous_count):
    if previous_count != 0:
        percentage_difference = ((current_count - previous_count) / previous_count) * 100
    else:
        percentage_difference = 0

    return percentage_difference


def get_monthly_new_buyers(supplier):
    now = datetime.now()
    current_month = now.month
    previous_month = (now.replace(day=1) - timedelta(days=1)).month

    current_month_new_buyers = get_new_buyer_count(supplier, current_month)
    previous_month_new_buyers = get_new_buyer_count(supplier, previous_month)

    percentage_difference = calculate_percentage_difference(
        current_month_new_buyers, previous_month_new_buyers
    )

    return current_month_new_buyers, percentage_difference
