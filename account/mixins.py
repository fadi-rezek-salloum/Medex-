from rest_framework.exceptions import PermissionDenied


class CheckGroupMixin:
    def __init__(self, allowed_group_names):
        self.allowed_group_names = allowed_group_names

    def check_permissions(self, request):
        if not request.user.groups.filter(name__in=self.allowed_group_names).exists():
            raise PermissionDenied()


class CheckSupplierAdminGroupMixin(CheckGroupMixin):
    def __init__(self):
        super().__init__(allowed_group_names=["Supplier Admin"])


class CheckBuyerAdminGroupMixin(CheckGroupMixin):
    def __init__(self):
        super().__init__(allowed_group_names=["Buyer Admin"])
