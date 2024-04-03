import uuid

from common.utils.file_upload_paths import withdraw_approve_receipt_path
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from order.models import Order, ReturnRequest

User = get_user_model()


class Wallet(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True, unique=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.full_name} - Balance: {str(self.balance)}"


class Transaction(models.Model):
    class TRANSACTION_TYPES_CHOICES(models.TextChoices):
        P = "P", _("Purchase")
        R = "R", _("Return")
        W = "W", _("Withdrawal")

    class TRANSACTION_STATUS_CHOICES(models.TextChoices):
        A = "A", _("Approved")
        D = "D", _("Denied")
        P = "P", _("Pending")

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True, unique=True
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES_CHOICES)
    transaction_status = models.CharField(
        max_length=20, choices=TRANSACTION_STATUS_CHOICES, null=True, blank=True
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    return_order = models.ForeignKey(
        ReturnRequest, on_delete=models.CASCADE, null=True, blank=True
    )

    receipt = models.FileField(upload_to=withdraw_approve_receipt_path, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} -> {str(self.amount)}"

    class Meta:
        ordering = ["-created"]
