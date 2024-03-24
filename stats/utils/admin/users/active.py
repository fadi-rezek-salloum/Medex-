import datetime

from django.contrib.auth import get_user_model

User = get_user_model()


def get_daily_active_users():
    today = datetime.date.today()
    last_seven_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]

    daily_active_buyers = []
    daily_active_suppliers = []
    for day in last_seven_days:
        buyers_count = User.objects.filter(is_buyer=True, last_login__date=day).count()
        suppliers_count = User.objects.filter(is_supplier=True, last_login__date=day).count()
        daily_active_buyers.append(buyers_count)
        daily_active_suppliers.append(suppliers_count)

    return {
        "days": [day.strftime("%A") for day in last_seven_days],
        "buyers": daily_active_buyers,
        "suppliers": daily_active_suppliers,
    }


def get_monthly_active_users():
    today = datetime.date.today()
    current_year = today.year
    months_of_year = [
        datetime.date(current_year, month, 1).strftime("%B") for month in range(1, 13)
    ]

    monthly_active_buyers = []
    monthly_active_suppliers = []
    for month in range(1, 13):
        buyers_count = User.objects.filter(
            is_buyer=True, last_login__year=current_year, last_login__month=month
        ).count()
        suppliers_count = User.objects.filter(
            is_supplier=True, last_login__year=current_year, last_login__month=month
        ).count()
        monthly_active_buyers.append(buyers_count)
        monthly_active_suppliers.append(suppliers_count)

    return {
        "months": months_of_year,
        "buyers": monthly_active_buyers,
        "suppliers": monthly_active_suppliers,
    }


def get_yearly_active_users():
    today = datetime.date.today()
    earliest_year = (
        User.objects.filter(last_login__isnull=False)
        .order_by("last_login")
        .first()
        .last_login.year
    )

    year_range = range(earliest_year, today.year + 1)

    yearly_active_buyers = []
    yearly_active_suppliers = []
    for year in year_range:
        buyers_count = User.objects.filter(is_buyer=True, last_login__year=year).count()
        suppliers_count = User.objects.filter(is_supplier=True, last_login__year=year).count()
        yearly_active_buyers.append(buyers_count)
        yearly_active_suppliers.append(suppliers_count)

    return {
        "years": list(year_range),
        "buyers": yearly_active_buyers,
        "suppliers": yearly_active_suppliers,
    }
