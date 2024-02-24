from rest_framework.exceptions import PermissionDenied


class CheckChatManagerGroupMixin:
    allowed_group_names = [
        "Supplier Chat",
        "Supplier Admin",
        "Buyer Chat",
        "Buyer Admin",
    ]

    def has_permission(self, request, view):
        """
        Check if the user has the necessary group membership.
        """
        if not request.user.groups.filter(name__in=self.allowed_group_names).exists():
            raise PermissionDenied()
        return True
