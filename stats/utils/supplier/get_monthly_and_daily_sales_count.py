import datetime

from django.db.models import F, IntegerField, Sum
from django.db.models.functions import ExtractDay
from order.models import Order


def get_monthly_and_daily_sales_count(user):
    today = datetime.date.today()

    last_seven_days = [today - datetime.timedelta(days=i) for i in range(7)]

    daily_sales_data = (
        Order.objects.filter(
            products__product__supplier=user,
            created__date__gte=today - datetime.timedelta(days=6),
            created__date__lte=today,
        )
        .annotate(day=ExtractDay(F("created")))
        .values("day")
        .annotate(total_sales_count=Sum(F("products__quantity"), output_field=IntegerField()))
        .order_by("day")
        .values("day", "total_sales_count")
    )

    daily_sales_count = []

    existing_data = {data["day"]: data["total_sales_count"] for data in daily_sales_data}
    for day in last_seven_days:
        if day.day in existing_data:
            daily_sales_count.append(existing_data[day.day])
        else:
            daily_sales_count.append(0)

    daily_sales_count.reverse()

    return daily_sales_count
