from account.models import User
from django.db.models import Count, Q


def get_users_count():
    buyers_and_suppliers = (
        User.objects.filter(Q(is_buyer=True) | Q(is_supplier=True), parent=None)
        .values("is_buyer", "is_supplier")
        .annotate(count=Count("id"))
    )

    buyers_count = sum(item["count"] for item in buyers_and_suppliers if item["is_buyer"])
    suppliers_count = sum(item["count"] for item in buyers_and_suppliers if item["is_supplier"])

    return {
        "buyers": buyers_count,
        "suppliers": suppliers_count,
    }
