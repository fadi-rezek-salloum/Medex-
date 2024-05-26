from django.contrib.auth import get_user_model
from django.db.models import Sum
from order.models import OrderItem, ReturnRequest

User = get_user_model()


def get_top_buyers_statistics(supplier):
    not_requested_or_declined = ReturnRequest.objects.filter(
        status__in=[
            ReturnRequest.RETURN_STATUS_CHOICES.NOT,
            ReturnRequest.RETURN_STATUS_CHOICES.DECLINED,
        ]
    )

    top_buyers = (
        User.objects.filter(
            orders__products__product__supplier=supplier,
            orders__products__shipping_status=OrderItem.SHIPPING_STATUS_CHOICES.DE,
            orders__products__in=OrderItem.objects.exclude(
                returnrequest__in=not_requested_or_declined
            ),
        )
        .annotate(total_spent=Sum("orders__products__total_price"))
        .order_by("-total_spent")[:3]
    )

    top_buyers_statistics = []

    for buyer in top_buyers:
        total_spent = buyer.total_spent
        buyer_name = buyer.full_name

        buyer_statistics = {
            "buyer_name": buyer_name,
            "total_spent": total_spent,
        }

        top_buyers_statistics.append(buyer_statistics)

    return top_buyers_statistics
