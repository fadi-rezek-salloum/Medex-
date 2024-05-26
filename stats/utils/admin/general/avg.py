import datetime

from django.db.models import Sum
from order.models import Order


def get_avg_income():
    today = datetime.date.today()

    num_orders_today = Order.objects.filter(created__date=today).count()
    total_money_paid_today = (
        Order.objects.filter(created__date=today).aggregate(total=Sum("products__total_price"))[
            "total"
        ]
        or 0
    )

    num_orders_this_month = Order.objects.filter(
        created__year=today.year, created__month=today.month
    ).count()
    total_money_paid_this_month = (
        Order.objects.filter(created__year=today.year, created__month=today.month).aggregate(
            total=Sum("products__total_price")
        )["total"]
        or 0
    )

    num_orders_this_year = Order.objects.filter(created__year=today.year).count()
    total_money_paid_this_year = (
        Order.objects.filter(created__year=today.year).aggregate(
            total=Sum("products__total_price")
        )["total"]
        or 0
    )

    avg_money_paid_per_order_today = (
        total_money_paid_today / num_orders_today if num_orders_today else 0
    )
    avg_money_paid_per_order_this_month = (
        total_money_paid_this_month / num_orders_this_month if num_orders_this_month else 0
    )
    avg_money_paid_per_order_this_year = (
        total_money_paid_this_year / num_orders_this_year if num_orders_this_year else 0
    )

    return {
        "day": round(avg_money_paid_per_order_today, 2),
        "month": round(avg_money_paid_per_order_this_month, 2),
        "year": round(avg_money_paid_per_order_this_year, 2),
    }
