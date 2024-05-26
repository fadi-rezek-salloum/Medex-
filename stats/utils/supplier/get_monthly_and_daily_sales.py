import calendar
import datetime

from django.db.models import Case, DecimalField, F, Sum, When
from django.db.models.functions import ExtractDay, ExtractMonth
from order.models import Order


def get_monthly_and_daily_sales(user):
    current_year = datetime.date.today().year
    today = datetime.date.today()

    last_seven_days = [today - datetime.timedelta(days=i) for i in range(7)]

    monthly_sales_data = (
        Order.objects.filter(products__product__supplier=user, created__year=current_year)
        .annotate(month=ExtractMonth(F("created")))
        .values("month")
        .annotate(
            total_sales=Sum(
                Case(
                    When(
                        products__product__sale_price__gt=0,
                        then=F("products__product__sale_price") * F("products__quantity"),
                    ),
                    default=F("products__product__price") * F("products__quantity"),
                    output_field=DecimalField(),
                )
            )
        )
        .order_by("month")
        .values("month", "total_sales")
    )

    daily_sales_data = (
        Order.objects.filter(
            products__product__supplier=user,
            created__year=current_year,
            created__date__gte=today - datetime.timedelta(days=6),
            created__date__lte=today,
        )
        .annotate(day=ExtractDay(F("created")))
        .values("day")
        .annotate(total_sales=Sum("products__total_price"))
        .order_by("day")
        .values("day", "total_sales")
    )

    months = []
    monthly_sales = []
    days = []
    daily_sales = []

    for data in monthly_sales_data:
        months.append(calendar.month_name[data["month"]])
        monthly_sales.append(data["total_sales"])

    existing_days = {data["day"]: data["total_sales"] for data in daily_sales_data}
    for day in last_seven_days:
        if day.day in existing_days:
            days.append(day.strftime("%A"))
            daily_sales.append(existing_days[day.day])
        else:
            days.append(day.strftime("%A"))
            daily_sales.append(0)

    days.reverse()
    daily_sales.reverse()

    return months, days, monthly_sales, daily_sales
