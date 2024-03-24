import datetime

from django.db.models import F, IntegerField, Min, Sum
from django.db.models.functions import ExtractDay, ExtractYear
from order.models import Order


def get_monthly_income():
    today = datetime.date.today()
    current_year = today.year

    months_of_year = [
        datetime.date(current_year, month, 1).strftime("%B") for month in range(1, 13)
    ]

    monthly_income = []
    for month in range(1, 13):
        sales_data = Order.objects.filter(
            created__year=current_year,
            created__month=month,
        ).aggregate(total_income=Sum(F("products__total_price"), output_field=IntegerField()))

        income = sales_data["total_income"] if sales_data["total_income"] is not None else 0
        monthly_income.append(income)

    return {"months": months_of_year, "values": monthly_income}


def get_yearly_income():
    today = datetime.date.today()

    earliest_year = Order.objects.aggregate(min_year=Min(ExtractYear("created__date")))[
        "min_year"
    ]

    year_range = range(earliest_year, today.year + 1)

    yearly_sales_data = (
        Order.objects.filter(
            created__date__year__gte=earliest_year,
            created__date__lte=today,
        )
        .annotate(year=ExtractYear(F("created__date")))
        .values("year")
        .annotate(total_income=Sum(F("products__total_price"), output_field=IntegerField()))
        .order_by("year")
        .values("year", "total_income")
    )

    yearly_income = {data["year"]: data["total_income"] for data in yearly_sales_data}

    income_by_year = [yearly_income.get(year, 0) for year in year_range]

    return {"years": list(year_range), "values": income_by_year}


def get_daily_income():
    today = datetime.date.today()

    last_seven_days = [
        (today - datetime.timedelta(days=i)).strftime("%A") for i in range(6, -1, -1)
    ]

    daily_sales_data = (
        Order.objects.filter(
            created__date__gte=today - datetime.timedelta(days=6),
            created__date__lte=today,
        )
        .annotate(day=ExtractDay(F("created")))
        .values("day")
        .annotate(total_income=Sum(F("products__total_price"), output_field=IntegerField()))
        .order_by("day")
        .values("day", "total_income")
    )

    daily_income = []
    existing_data = {data["day"]: data["total_income"] for data in daily_sales_data}

    for day_name in last_seven_days:
        if day_name in existing_data:
            daily_income.append(existing_data[day_name])
        else:
            daily_income.append(0)

    return {"days": last_seven_days, "values": daily_income}
