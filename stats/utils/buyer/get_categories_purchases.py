from django.db.models import Sum
from order.models import OrderItem


def get_categories_purchases(user):
    category_purchases = (
        OrderItem.objects.filter(user=user, product__category__isnull=False)
        .values("product__category__name")
        .annotate(total_purchases=Sum("quantity"))
    )

    categories = []
    total_purchases = []

    for i in category_purchases:
        categories.append(i["product__category__name"])
        total_purchases.append(i["total_purchases"])

    return categories, total_purchases
