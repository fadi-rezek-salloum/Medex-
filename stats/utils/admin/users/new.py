import datetime

from django.contrib.auth import get_user_model
from django.db.models import Min

User = get_user_model()


def get_daily_new_users():
    today = datetime.date.today()
    last_seven_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]

    daily_new_buyers = []
    daily_new_suppliers = []
    for day in last_seven_days:
        buyers_count = User.objects.filter(is_buyer=True, created__date=day).count()
        suppliers_count = User.objects.filter(is_supplier=True, created__date=day).count()
        daily_new_buyers.append(buyers_count)
        daily_new_suppliers.append(suppliers_count)

    return {
        "days": [day.strftime("%A") for day in last_seven_days],
        "buyers": daily_new_buyers,
        "suppliers": daily_new_suppliers,
    }


def get_monthly_new_users():
    today = datetime.date.today()
    current_year = today.year
    months_of_year = [
        datetime.date(current_year, month, 1).strftime("%B") for month in range(1, 13)
    ]

    monthly_new_buyers = []
    monthly_new_suppliers = []
    for month in range(1, 13):
        buyers_count = User.objects.filter(
            is_buyer=True, created__year=current_year, created__month=month
        ).count()
        suppliers_count = User.objects.filter(
            is_supplier=True, created__year=current_year, created__month=month
        ).count()
        monthly_new_buyers.append(buyers_count)
        monthly_new_suppliers.append(suppliers_count)

    return {
        "months": months_of_year,
        "buyers": monthly_new_buyers,
        "suppliers": monthly_new_suppliers,
    }


def get_yearly_new_users():
    today = datetime.date.today()
    earliest_year = User.objects.aggregate(min_year=Min("created__year")).get(
        "min_year", today.year
    )

    year_range = range(earliest_year, today.year + 1)

    yearly_new_buyers = []
    yearly_new_suppliers = []
    for year in year_range:
        buyers_count = User.objects.filter(is_buyer=True, created__year=year).count()
        suppliers_count = User.objects.filter(is_supplier=True, created__year=year).count()
        yearly_new_buyers.append(buyers_count)
        yearly_new_suppliers.append(suppliers_count)

    return {
        "years": list(year_range),
        "buyers": yearly_new_buyers,
        "suppliers": yearly_new_suppliers,
    }
