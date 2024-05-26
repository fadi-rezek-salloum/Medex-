import datetime

from django.db.models import Min, Sum
from quote.models import QuoteOffer


def get_daily_accepted_offers_value():
    today = datetime.date.today()
    last_seven_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]

    daily_accepted_offers_value = []
    for day in last_seven_days:
        accepted_offers = QuoteOffer.objects.filter(
            status="A", created__date=day
        ).select_related("quote__quoteproduct_set")

        if accepted_offers.exists():
            total_value = (
                accepted_offers.aggregate(
                    total_new_price=Sum("quote__quoteproduct_set__new_price")
                )["total_new_price"]
                or 0
            )
        else:
            total_value = 0

        daily_accepted_offers_value.append(total_value)

    return {
        "days": [day.strftime("%A") for day in last_seven_days],
        "values": daily_accepted_offers_value,
    }


def get_monthly_accepted_offers_value():
    today = datetime.date.today()
    current_year = today.year
    months_of_year = [
        datetime.date(current_year, month, 1).strftime("%B") for month in range(1, 13)
    ]

    monthly_accepted_offers_value = []
    for month in range(1, 13):
        accepted_offers = QuoteOffer.objects.filter(
            status="A", created__year=current_year, created__month=month
        )

        if accepted_offers.exists():
            total_value = (
                accepted_offers.aggregate(
                    total_new_price=Sum("quote__quoteproduct_set__new_price")
                )["total_new_price"]
                or 0
            )
        else:
            total_value = 0

        monthly_accepted_offers_value.append(float(total_value))

    return {
        "months": months_of_year,
        "values": monthly_accepted_offers_value,
    }


def get_yearly_accepted_offers_value():
    today = datetime.date.today()
    earliest_year = QuoteOffer.objects.aggregate(min_year=Min("created__year")).get(
        "min_year", today.year
    )

    if not earliest_year:
        earliest_year = today.year

    year_range = range(earliest_year, today.year + 1)

    yearly_accepted_offers_value = []
    for year in year_range:
        accepted_offers = QuoteOffer.objects.filter(status="A", created__year=year)

        if accepted_offers.exists():
            total_value = (
                accepted_offers.aggregate(
                    total_new_price=Sum("quote__quoteproduct_set__new_price")
                )["total_new_price"]
                or 0
            )
        else:
            total_value = 0

        yearly_accepted_offers_value.append(float(total_value))

    return {
        "years": list(year_range),
        "values": yearly_accepted_offers_value,
    }
