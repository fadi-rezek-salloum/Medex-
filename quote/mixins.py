from rest_framework.exceptions import PermissionDenied


class CheckQuoteManagerGroupMixin:
    allowed_group_names = [
        "Supplier Quote Manager",
        "Supplier Admin",
        "Buyer Quote Manager",
        "Buyer Admin",
    ]

    def check_permissions(self, request):
        if not request.user.groups.filter(name__in=self.allowed_group_names).exists():
            raise PermissionDenied()
