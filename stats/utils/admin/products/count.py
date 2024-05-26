from django.db.models import Sum
from product.models import Product


def get_in_stock_products_count():
    total_products = Product.objects.filter(is_available=True).aggregate(
        total_count=Sum("stock_quantity")
    )

    return total_products["total_count"] or 0


def get_out_of_stock_products_count():
    total_products = Product.objects.filter(is_available=False).aggregate(
        total_count=Sum("stock_quantity")
    )

    return total_products["total_count"] or 0
