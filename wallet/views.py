from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Transaction, Wallet
from .serializers import TransactionSerializer, WalletSerializer
from .services import TransactionService


class WalletRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

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
        transaction_serializer = TransactionSerializer(transactions, many=True)

        context = {
            "wallet": wallet_serializer.data,
            "transactions": transaction_serializer.data,
        }

        return Response(context)


class TransactionCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            TransactionService.create_transaction(**serializer.validated_data)
            return Response(
                {"message": "Transaction created successfully"}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WithdrawAPIView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        mutable_data["transaction_type"] = Transaction.TRANSACTION_TYPES_CHOICES.W
        mutable_data["user"] = request.user.id

        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            return Response(
                {"error": "User does not have a wallet"}, status=status.HTTP_400_BAD_REQUEST
            )

        mutable_data["wallet"] = wallet.id

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        if wallet.balance - amount < 0:
            return Response(
                {"error": "Withdrawal amount exceeds wallet balance"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_withdrawals = TransactionService.calculate_total_withdrawals_amount(wallet)
        if total_withdrawals + amount > wallet.balance:
            return Response(
                {"error": "Total withdrawals exceed wallet balance"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(
            user=request.user,
            wallet=wallet,
            transaction_type=Transaction.TRANSACTION_TYPES_CHOICES.W,
            transaction_status=Transaction.TRANSACTION_STATUS_CHOICES.P,
        )

        return Response({"message": "Withdrawal successful"}, status=status.HTTP_201_CREATED)
