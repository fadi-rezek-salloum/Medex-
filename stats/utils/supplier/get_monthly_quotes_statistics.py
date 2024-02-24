from django.utils import timezone
from quote.models import QuoteOffer


def get_monthly_quotes_statistics(supplier):
    current_month = timezone.now().month
    current_year = timezone.now().year

    monthly_statistics = []

    for month in range(1, 13):
        quote_offers = QuoteOffer.objects.filter(
            user=supplier, created__month=month, created__year=current_year
        )

        total_quotes = quote_offers.count()

        total_approved_quotes = quote_offers.filter(
            status=QuoteOffer.STATUS_CHOICES.APPROVED
        ).count()

        total_declined_quotes = quote_offers.filter(
            status=QuoteOffer.STATUS_CHOICES.DENIED
        ).count()

        total_pending_quotes = quote_offers.filter(
            status=QuoteOffer.STATUS_CHOICES.PENDING
        ).count()

        statistics = {
            "month": month,
            "total_quotes": total_quotes,
            "total_approved_quotes": total_approved_quotes,
            "total_declined_quotes": total_declined_quotes,
            "total_pending_quotes": total_pending_quotes,
        }

        if month > current_month:
            statistics = {
                "month": month,
                "total_quotes": 0,
                "total_approved_quotes": 0,
                "total_declined_quotes": 0,
                "total_pending_quotes": 0,
            }

        monthly_statistics.append(statistics)

    return monthly_statistics
