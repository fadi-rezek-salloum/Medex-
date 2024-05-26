from datetime import datetime

from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth
from wallet.models import Transaction


def get_monthly_transactions_by_status(user):
    approved_counts = [0] * 12
    denied_counts = [0] * 12
    pending_counts = [0] * 12

    transactions_by_month = (
        Transaction.objects.filter(user=user, created__year=datetime.now().year)
        .annotate(
            month=ExtractMonth("created"),
        )
        .values("month")
        .annotate(
            approved_count=Count("id", filter=Q(transaction_status="A")),
            denied_count=Count("id", filter=Q(transaction_status="D")),
            pending_count=Count("id", filter=Q(transaction_status="P")),
        )
        .order_by("month")
    )

    for transaction in transactions_by_month:
        month_index = transaction["month"] - 1
        approved_counts[month_index] = transaction["approved_count"]
        denied_counts[month_index] = transaction["denied_count"]
        pending_counts[month_index] = transaction["pending_count"]

    return approved_counts, denied_counts, pending_counts
