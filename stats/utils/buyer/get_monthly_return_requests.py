import datetime

from order.models import ReturnRequest


def get_monthly_return_requests(user):
    current_month = datetime.date.today().month

    monthly_return_requests = ReturnRequest.objects.filter(
        user=user,
        created__month=current_month,
        status=ReturnRequest.RETURN_STATUS_CHOICES.APPROVED,
    ).count()

    return monthly_return_requests
