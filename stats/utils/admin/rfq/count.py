from quote.models import QuoteOffer, QuoteRequest


def get_quotes_status_count(status):
    count = QuoteOffer.objects.filter(status=status).count()
    return count


def get_total_quotes_count():
    total_quotes_count = QuoteRequest.objects.count()
    return total_quotes_count


def get_total_approved_quotes_count():
    return get_quotes_status_count("A")


def get_total_rejected_quotes_count():
    return get_quotes_status_count("D")


def get_total_pending_quotes_count():
    return get_quotes_status_count("P")
