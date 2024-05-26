import statistics

from django.utils import timezone
from order.models import OrderItem


def calculate_order_statistics(supplier):
    now = timezone.now()
    current_month = now.month
    previous_month = (now.replace(day=1) - timezone.timedelta(days=1)).month

    current_month_items = OrderItem.objects.filter(
        product__supplier=supplier, created__month=current_month
    )
    current_prices = [item.get_total_product_price() for item in current_month_items]

    current_statistics = {}

    if current_prices:
        current_statistics["highest_sale"] = max(current_prices)
        current_statistics["lowest_sale"] = min(current_prices)
        current_statistics["average_sale"] = statistics.mean(current_prices)
    else:
        current_statistics["highest_sale"] = 0
        current_statistics["lowest_sale"] = 0
        current_statistics["average_sale"] = 0

    percentage_difference = {}
    for key, current_value in current_statistics.items():
        previous_value = None
        if previous_month:
            previous_month_items = OrderItem.objects.filter(
                product__supplier=supplier, created__month=previous_month
            )
            previous_prices = [item.get_total_product_price() for item in previous_month_items]
            previous_value = statistics.mean(previous_prices) if previous_prices else 0

        if previous_value != 0:
            percentage_difference[key] = (
                (current_value - previous_value) / previous_value
            ) * 100
        else:
            percentage_difference[key] = 0

    return current_statistics, percentage_difference
