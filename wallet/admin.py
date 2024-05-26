from django.contrib import admin, messages
from unfold.admin import ModelAdmin

from .models import Transaction, Wallet


@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ("id", "user", "transaction_type", "transaction_status", "amount", "created")
    list_filter = ("transaction_type", "transaction_status", "created")

    def save_model(self, request, obj, form, change):
        if change:
            new_status = obj.transaction_status

            if new_status != Transaction.TRANSACTION_STATUS_CHOICES.P:
                messages.set_level(request, messages.ERROR)
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Cannot change status of an already approved / declined transaction.",
                )
                return

        if (
            obj.transaction_type == Transaction.TRANSACTION_TYPES_CHOICES.W
            and obj.transaction_status == Transaction.TRANSACTION_STATUS_CHOICES.A
        ):
            if not obj.receipt:
                messages.set_level(request, messages.ERROR)
                messages.add_message(
                    request,
                    messages.ERROR,
                    "A receipt must be uploaded for an approved withdrawal transaction.",
                )

            wallet = Wallet.objects.get(id=obj.wallet_id)
            if wallet.balance - obj.amount < 0:
                messages.set_level(request, messages.ERROR)
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Approving this withdrawal would result in a negative balance.",
                )
            else:
                wallet.balance -= obj.amount
                wallet.save()

            super().save_model(request, obj, form, change)
