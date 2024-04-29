import json
from datetime import datetime

from account.serializers import AddressSerializer
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .mixins import CheckQuoteManagerGroupMixin
from .models import QuoteOffer, QuoteRequest
from .serializers import QuoteAttachmentSerializer, QuoteOfferSerializer, QuoteSerializer


class ListCreateQuoteView(CheckQuoteManagerGroupMixin, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuoteSerializer
    queryset = QuoteRequest.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            attachments = request.data.pop("attachments", [])
            products = request.data.pop("products", [])
        except Exception:
            attachments = []
            products = []

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        quote = serializer.save(user=request.user)

        quote.products.set(products)

        for attachment in attachments:
            attachment_serializer = QuoteAttachmentSerializer(
                data={"quote": quote.id, "attachment": attachment}
            )
            attachment_serializer.is_valid(raise_exception=True)
            attachment_serializer.save()

        return Response(status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = super().get_queryset()
        user = (
            self.request.user.parent
            if self.request.user.parent is not None
            else self.request.user
        )
        now = datetime.now()

        if user.is_buyer:
            return qs.filter(user__parent=user if user.parent else user, due_date__gte=now)
        elif user.is_supplier:
            return qs.filter(
                Q(supplier=user.parent if user.parent else user) | Q(supplier__isnull=True),
                due_date__gte=now,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ListCreateQuoteOfferView(CheckQuoteManagerGroupMixin, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = QuoteOffer.objects.all()
    serializer_class = QuoteOfferSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()

            delivery_address = AddressSerializer(data=json.loads(data["delivery_address"]))
            delivery_address.is_valid(raise_exception=True)
            data["delivery_address"] = delivery_address.save().id

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            offer = serializer.save()
            offer.user = request.user
            offer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as ex:
            print(ex)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_buyer and self.request.GET.get("id") is not None:
            return qs.filter(
                Q(quote__user=self.request.user) | Q(quote__user=self.request.user.parent),
                quote__id=self.request.GET.get("id"),
            ).distinct()
        elif self.request.user.is_supplier:

            return (
                qs.filter(Q(user=self.request.user) | Q(user=self.request.user.parent))
                .distinct()
                .exclude(quote__user=self.request.user)
                .exclude(quote__user=self.request.user.parent)
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)


class RetrieveQuoteOfferView(CheckQuoteManagerGroupMixin, RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = QuoteOffer.objects.all()
    serializer_class = QuoteOfferSerializer
    lookup_field = "id"

    def post(self, request, *args, **kwargs):
        type_mapping = {
            "approve": "A",
            "decline": "D",
        }

        type_value = request.data.get("type")

        if type_value and type_value in type_mapping:
            q = self.get_object()
            q.status = type_mapping[type_value]
            q.save()

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


# CheckQuoteManagerGroupMixin
class RetrieveUpdateInvoiceViewSet(ModelViewSet):
    serializer_class = QuoteOfferSerializer
    queryset = QuoteOffer.objects.all()
    http_method_names = ["GET", "PUT"]
    permission_classes = [
        IsAuthenticated,
    ]

    # def get(self, request, pk=None):
    #     if pk:
    #         try:
    #             instance = QuoteOffer.objects.get(pk=pk)
    #             serializer = QuoteOfferSerializer(instance)
    #             return Response(serializer.data)
    #         except QuoteOffer.DoesNotExist:
    #             return Response(status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         queryset = QuoteOffer.objects.all()
    #         serializer = QuoteOfferSerializer(queryset, many=True)
    #         return Response(serializer.data)

    # def put(self, request, pk):
    #     try:
    #         instance = QuoteOffer.objects.get(pk=pk)
    #         serializer = QuoteOfferSerializer(instance, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except QuoteOffer.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
