import calendar
import datetime

from django.db.models import F, Sum
from django.db.models.functions import ExtractMonth
from order.models import Order


def get_yearly_payments_per_month(user):
    current_year = datetime.date.today().year

    yearly_payments = (
        Order.objects.filter(user=user, created__year=current_year)
        .annotate(month=ExtractMonth(F("created")))
        .values("month")
        .annotate(total_money=Sum("products__total_price"))
        .order_by("-month")
    )

    months = []
    yearly_payments_per_month = []

    for i in yearly_payments:
        months.append(calendar.month_name[i["month"]])
        yearly_payments_per_month.append(i["total_money"])

    return months, yearly_payments_per_month
