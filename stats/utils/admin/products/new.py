import datetime

from product.models import Product


def get_daily_new_products():
    today = datetime.date.today()
    last_seven_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]

    daily_new_products = []
    for day in last_seven_days:
        new_products_count = Product.objects.filter(created__date=day).count()
        daily_new_products.append(new_products_count)

    return {
        "days": [day.strftime("%A") for day in last_seven_days],
        "new_products": daily_new_products,
    }


def get_monthly_new_products():
    today = datetime.date.today()
    current_year = today.year
    months_of_year = [
        datetime.date(current_year, month, 1).strftime("%B") for month in range(1, 13)
    ]

    monthly_new_products = []
    for month in range(1, 13):
        new_products_count = Product.objects.filter(
            created__year=current_year, created__month=month
        ).count()
        monthly_new_products.append(new_products_count)

    return {
        "months": months_of_year,
        "new_products": monthly_new_products,
    }


def get_yearly_new_products():
    today = datetime.date.today()

    earliest_product = Product.objects.filter(created__isnull=False).order_by("created").first()

    if not earliest_product:
        return {"years": [], "new_products": []}

    earliest_year = earliest_product.created.year
    year_range = range(earliest_year, today.year + 1)

    yearly_new_products = []
    for year in year_range:
        new_products_count = Product.objects.filter(created__year=year).count()
        yearly_new_products.append(new_products_count)

    return {
        "years": list(year_range),
        "new_products": yearly_new_products,
    }
