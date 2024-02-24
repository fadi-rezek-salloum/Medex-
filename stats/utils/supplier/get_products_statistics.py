from django.db.models import Sum
from product.models import Category, Product


def get_total_products_count(supplier):
    total_products = Product.objects.filter(supplier=supplier).aggregate(
        total_count=Sum("stock_quantity")
    )

    return total_products["total_count"] or 0


def get_products_per_category(supplier):
    category_names = []
    product_counts = []
    categories = Category.objects.filter(products__supplier=supplier).distinct()

    for category in categories:
        product_count = Product.objects.filter(category=category, supplier=supplier).aggregate(
            total_count=Sum("stock_quantity")
        )
        category_names.append(category.name)
        product_counts.append(product_count["total_count"] or 0)

    return category_names, product_counts
