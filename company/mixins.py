from rest_framework.exceptions import PermissionDenied


class CheckSupplierAdminGroupMixin:
    allowed_group_names = [
        "Supplier Admin",
    ]

    def check_permissions(self, request):
        if not request.method == "GET":
            if not request.user.groups.filter(name__in=self.allowed_group_names).exists():
                raise PermissionDenied()
