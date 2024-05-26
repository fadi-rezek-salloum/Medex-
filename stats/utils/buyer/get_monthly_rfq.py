import datetime

from django.db.models import Count
from quote.models import QuoteOffer, QuoteRequest


def get_monthly_rfq(user):
    current_month = datetime.date.today().month

    monthly_quote_requests = QuoteRequest.objects.filter(
        user=user,
        created__month=current_month,
        quoteoffer__status=QuoteOffer.STATUS_CHOICES.APPROVED,
    ).annotate(num_approved_quotes=Count("quoteoffer"))

    return monthly_quote_requests
