from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from stats.utils.shared.get_monthly_transactions_by_status import (
    get_monthly_transactions_by_status,
)

from .models import Wallet
from .pagination import TransactionsPagination
from .serializers import TransactionSerializer, WalletSerializer
from .services import TransactionService


class WalletRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TransactionsPagination

    def get_object(self):
        user = self.request.user
        if user.parent is None:
            return user.wallet
        else:
            return user.parent.wallet

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        wallet_serializer = self.get_serializer(instance)

        transactions = TransactionService.retrieve_transactions_by_wallet(wallet=instance)
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)

            response_data = {
                "wallet": wallet_serializer.data,
                "transactions": serializer.data,
                "stats": self._calculate_stats(instance, transactions),
            }

        return self.get_paginated_response(response_data)

    def _calculate_stats(self, instance, transactions):
        """Encapsulates stats calculations for better readability."""
        total_transactions = transactions.count()
        total_withdrawal_amount = TransactionService.calculate_total_withdrawals_amount(
            wallet=instance, status="A"
        )
        pending_transactions = TransactionService.retrieve_transactions_by_status(
            wallet=instance, status="P"
        ).count()
        accepted_transactions = TransactionService.retrieve_transactions_by_status(
            wallet=instance, status="A"
        ).count()

        monthly_transactions = get_monthly_transactions_by_status(instance.user)

        return {
            "total_transactions": total_transactions,
            "total_withdrawal_amount": total_withdrawal_amount,
            "pending_transactions": pending_transactions,
            "accepted_transactions": accepted_transactions,
            "monthly_accepted_transactions": monthly_transactions[0],
            "monthly_denied_transactions": monthly_transactions[1],
            "monthly_pending_transactions": monthly_transactions[2],
        }


class WithdrawAPIView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        mutable_data["transaction_type"] = "W"
        mutable_data["user"] = str(request.user.id)

        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            return Response(
                {"error": _("User does not have a wallet")}, status=status.HTTP_400_BAD_REQUEST
            )

        mutable_data["wallet"] = str(wallet.id)

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        if wallet.balance - amount < 0:
            return Response(
                {"error": _("Withdrawal amount exceeds wallet balance")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_withdrawals = TransactionService.calculate_total_withdrawals_amount(wallet=wallet)

        if total_withdrawals + amount > wallet.balance:
            return Response(
                {"error": _("Total withdrawals exceed wallet balance")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(
            transaction_status="P",
        )

        return Response(
            {
                "message": _("Withdrawal request was successfully submitted"),
                "transaction": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
