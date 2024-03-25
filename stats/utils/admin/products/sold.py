import datetime

from django.db.models import Sum
from order.models import OrderItem


def get_daily_sold_products():
    today = datetime.date.today()
    last_seven_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]

    daily_sold_products = []
    for day in last_seven_days:
        sold_products_count = (
            OrderItem.objects.filter(created__date=day).aggregate(
                total_quantity=Sum("quantity")
            )["total_quantity"]
            or 0
        )
        daily_sold_products.append(sold_products_count)

    return {
        "days": [day.strftime("%A") for day in last_seven_days],
        "sold_products": daily_sold_products,
    }


def get_monthly_sold_products():
    today = datetime.date.today()
    current_year = today.year
    months_of_year = [
        datetime.date(current_year, month, 1).strftime("%B") for month in range(1, 13)
    ]

    monthly_sold_products = []
    for month in range(1, 13):
        sold_products_count = (
            OrderItem.objects.filter(
                created__year=current_year, created__month=month
            ).aggregate(total_quantity=Sum("quantity"))["total_quantity"]
            or 0
        )
        monthly_sold_products.append(sold_products_count)

    return {
        "months": months_of_year,
        "sold_products": monthly_sold_products,
    }


def get_yearly_sold_products():
    today = datetime.date.today()
    earliest_year = (
        OrderItem.objects.filter(created__isnull=False).order_by("created").first().created.year
    )

    year_range = range(earliest_year, today.year + 1)

    yearly_sold_products = []
    for year in year_range:
        sold_products_count = (
            OrderItem.objects.filter(created__year=year).aggregate(
                total_quantity=Sum("quantity")
            )["total_quantity"]
            or 0
        )
        yearly_sold_products.append(sold_products_count)

    return {
        "years": list(year_range),
        "sold_products": yearly_sold_products,
    }
