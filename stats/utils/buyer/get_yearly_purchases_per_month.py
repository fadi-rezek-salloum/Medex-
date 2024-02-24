import calendar
import datetime

from django.db.models import Count, F
from django.db.models.functions import ExtractMonth
from order.models import Order


def get_yearly_purchases_per_month(user):
    current_year = datetime.date.today().year

    yearly_purchases = (
        Order.objects.filter(user=user, created__year=current_year)
        .annotate(month=ExtractMonth(F("created")))
        .annotate(total_purchases=Count("products__quantity"))
        .order_by("-month")
    )

    yearly_purchases_per_month = []

    for purchase in yearly_purchases:
        yearly_purchases_per_month.append(purchase.total_purchases)

    return yearly_purchases_per_month
