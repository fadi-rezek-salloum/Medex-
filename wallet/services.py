from django.db.models import Sum

from .models import Transaction, Wallet


class WalletService:
    @staticmethod
    def recharge_balance(wallet_id=None, wallet=None, amount=0):
        """
        Recharge the balance of a wallet and return the updated balance.
        """
        wallet = WalletService._get_wallet(wallet_id, wallet)
        wallet.balance += amount
        wallet.save()
        return wallet.balance

    @staticmethod
    def update_balance(wallet_id=None, wallet=None, new_balance=0):
        """
        Update the balance of a wallet and return the updated balance.
        """
        wallet = WalletService._get_wallet(wallet_id, wallet)
        wallet.balance = new_balance
        wallet.save()
        return wallet.balance

    @staticmethod
    def deduct_balance(wallet_id=None, wallet=None, amount=0):
        """
        Deduct an amount from the balance of a wallet and return the updated balance.
        Raise a ValueError if the balance is insufficient.
        """
        wallet = WalletService._get_wallet(wallet_id, wallet)
        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            return wallet.balance
        else:
            raise ValueError("Insufficient balance")

    @staticmethod
    def _get_wallet(wallet_id=None, wallet=None):
        """
        Get the wallet object based on wallet_id or wallet instance.
        """
        if wallet:
            return wallet
        try:
            return Wallet.objects.get(id=wallet_id)
        except Wallet.DoesNotExist:
            raise ValueError("Wallet not found")


class TransactionService:
    @staticmethod
    def create_transaction(
        user_id,
        wallet_id,
        amount,
        transaction_type,
        transaction_status=None,
        order=None,
        return_order=None,
    ):
        """
        Create a new transaction.
        """
        return Transaction.objects.create(
            user_id=user_id,
            wallet_id=wallet_id,
            amount=amount,
            transaction_type=transaction_type,
            transaction_status=transaction_status,
            order=order,
            return_order=return_order,
        )

    @staticmethod
    def retrieve_transactions_by_wallet(wallet_id=None, wallet=None):
        """
        Retrieve transactions associated with a wallet.
        """
        if wallet_id is None and wallet is None:
            raise ValueError("Either wallet_id or wallet instance must be provided")

        transactions = (
            Transaction.objects.filter(wallet_id=wallet_id)
            if wallet_id is not None
            else Transaction.objects.filter(wallet=wallet)
        )

        return transactions

    @staticmethod
    def retrieve_transaction_by_return_id(return_id=None, return_order=None):
        """
        Retrieve a transaction by return ID.
        """
        if return_id is None and return_order is None:
            raise ValueError("Either return_id or return_order instance must be provided")

        transaction = (
            Transaction.objects.filter(return_order__id=return_id).first()
            if return_id is not None
            else Transaction.objects.filter(return_order=return_order).first()
        )
        return transaction

    @staticmethod
    def calculate_total_withdrawals_amount(wallet_id=None, wallet=None):
        """
        Calculate the total amount of withdrawals for a wallet.
        """
        if wallet_id is None and wallet is None:
            raise ValueError("Either wallet_id or wallet instance must be provided")

        qs = (
            Transaction.objects.filter(
                wallet__id=wallet_id, transaction_type=Transaction.TRANSACTION_TYPES_CHOICES.W
            )
            if wallet_id is not None
            else Transaction.objects.filter(
                wallet=wallet, transaction_type=Transaction.TRANSACTION_TYPES_CHOICES.W
            )
        )

        total = qs.aggregate(total=Sum("amount"))["total"] or 0

        return total

    @staticmethod
    def approve_transaction(transaction_id=None, transaction=None):
        """
        Approve a transaction and handle balance change.
        """
        if transaction_id is None and transaction is None:
            raise ValueError("Either transaction_id or transaction instance must be provided")

        try:
            if not transaction:
                transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            raise ValueError("Transaction not found")

        if transaction.transaction_status == Transaction.TRANSACTION_STATUS_CHOICES.A:
            return

        transaction.transaction_status = Transaction.TRANSACTION_STATUS_CHOICES.A
        transaction.save()

        BalanceChangeService.handle_balance_change(transaction)

    @staticmethod
    def decline_transaction(transaction_id=None, transaction=None):
        """
        Decline a transaction.
        """
        if transaction_id is None and transaction is None:
            raise ValueError("Either transaction_id or transaction instance must be provided")

        try:
            if transaction is None:
                transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            raise ValueError("Transaction not found")

        if transaction.transaction_status == Transaction.TRANSACTION_STATUS_CHOICES.D:
            return
        transaction.transaction_status = Transaction.TRANSACTION_STATUS_CHOICES.D
        transaction.save()


class BalanceChangeService:
    @staticmethod
    def handle_balance_change(transaction_id=None, transaction=None):
        """
        Handle balance change based on transaction type.
        """
        if not transaction:
            try:
                transaction = Transaction.objects.get(id=transaction_id)
            except Transaction.DoesNotExist:
                raise ValueError("Transaction not found")

        wallet = transaction.wallet
        if transaction.transaction_type == Transaction.TRANSACTION_TYPES_CHOICES.W:
            BalanceChangeService.handle_withdrawal(transaction, wallet)
        elif transaction.transaction_type == Transaction.TRANSACTION_TYPES_CHOICES.R:
            BalanceChangeService.handle_recharge(transaction, wallet)
        else:
            return BalanceChangeService.handle_purchase(transaction, wallet)

    @staticmethod
    def handle_withdrawal(transaction, wallet):
        """
        Handle a withdrawal transaction.
        """
        if wallet.balance >= transaction.amount:
            WalletService.deduct_balance(wallet=wallet, amount=transaction.amount)
        else:
            raise ValueError("Insufficient balance")

    @staticmethod
    def handle_recharge(transaction, wallet):
        """
        Handle a recharge transaction.
        """
        WalletService.recharge_balance(wallet=wallet, amount=transaction.amount)

    @staticmethod
    def handle_purchase(transaction, wallet):
        """
        Handle a purchase transaction.
        """
        total_purchase_price = transaction.order.get_total()
        extra_charge = 0.0

        if wallet.balance >= transaction.amount:
            WalletService.deduct_balance(wallet=wallet, amount=transaction.amount)
        else:
            extra_charge = max(0, total_purchase_price - wallet.balance)
            WalletService.update_balance(wallet=wallet, new_balance=0)

        return extra_charge
