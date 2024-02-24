from datetime import datetime, timedelta

from chat.models import Thread
from django.db.models import Count


def get_total_threads(user, month):
    threads_count = (
        Thread.objects.by_user(
            user,
        )
        .filter(
            created__month=month,
        )
        .distinct()
        .aggregate(total_count=Count("id"))
    )

    return threads_count["total_count"] if threads_count["total_count"] else 0


def calculate_percentage_difference(current_threads, previous_threads):
    if previous_threads != 0:
        percentage_difference = ((current_threads - previous_threads) / previous_threads) * 100
    else:
        percentage_difference = 0

    return percentage_difference


def get_monthly_threads_count(user):
    now = datetime.now()
    current_month = now.month
    previous_month = (now.replace(day=1) - timedelta(days=1)).month

    current_month_threads = get_total_threads(user, current_month)
    previous_month_threads = get_total_threads(user, previous_month)

    percentage_difference = calculate_percentage_difference(
        current_month_threads, previous_month_threads
    )

    return current_month_threads, percentage_difference
