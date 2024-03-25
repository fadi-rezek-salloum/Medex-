import datetime

from django.db.models import Min, Sum
from quote.models import QuoteOffer


def get_daily_accepted_offers_value():
    today = datetime.date.today()
    last_seven_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]

    daily_accepted_offers_value = []
    for day in last_seven_days:
        total_value = (
            QuoteOffer.objects.filter(status="A", created__date=day)
            .aggregate(total_value=Sum("total_price"))
            .get("total_value", 0)
        )
        daily_accepted_offers_value.append(total_value or 0)

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
        total_value = (
            QuoteOffer.objects.filter(
                status="A", created__year=current_year, created__month=month
            )
            .aggregate(total_value=Sum("total_price"))
            .get("total_value", 0)
        )
        monthly_accepted_offers_value.append(float(total_value or 0))

    for _ in range(len(monthly_accepted_offers_value), 12):
        monthly_accepted_offers_value.append(0)

    return {"months": months_of_year, "values": monthly_accepted_offers_value}


def get_yearly_accepted_offers_value():
    today = datetime.date.today()
    earliest_year = QuoteOffer.objects.aggregate(min_year=Min("created__year")).get(
        "min_year", today.year
    )

    year_range = range(earliest_year, today.year + 1)

    yearly_accepted_offers_value = []
    for year in year_range:
        total_value = (
            QuoteOffer.objects.filter(status="A", created__year=year)
            .aggregate(total_value=Sum("total_price"))
            .get("total_value", 0)
        )
        yearly_accepted_offers_value.append(float(total_value or 0))

    return {"years": list(year_range), "values": yearly_accepted_offers_value}
