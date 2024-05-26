import json
from datetime import datetime

from account.serializers import AddressSerializer
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .mixins import CheckQuoteManagerGroupMixin
from .models import OfferProduct, QuoteOffer, QuoteProduct, QuoteRequest
from .pagination import QuoteOfferPagination
from .serializers import QuoteAttachmentSerializer, QuoteOfferSerializer, QuoteSerializer


class ListCreateQuoteView(CheckQuoteManagerGroupMixin, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuoteSerializer
    queryset = QuoteRequest.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        try:
            attachments = data.pop("attachments", [])
            product_data = data.pop("products", [])

            if not isinstance(product_data[0], dict):
                product_data = json.loads(product_data[0])
        except Exception as ex:
            print(ex)
            raise ValueError("There was an issue with products or with the attachments")

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        quote = serializer.save(user=request.user)

        for product_info in product_data:
            QuoteProduct.objects.create(**product_info, quote=quote)

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
            if user.parent is not None:
                return qs.filter(user__parent=user, due_date__gte=now)
            return qs.filter(user=user, due_date__gte=now)
        elif user.is_supplier:
            if user.parent is not None:
                return qs.filter(
                    Q(supplier=user.parent) | Q(supplier__isnull=True),
                    due_date__gte=now,
                )
            return qs.filter(
                Q(supplier=user) | Q(supplier__isnull=True),
                due_date__gte=now,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ListCreateQuoteOfferView(CheckQuoteManagerGroupMixin, ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = QuoteOffer.objects.all()
    serializer_class = QuoteOfferSerializer
    pagination_class = QuoteOfferPagination

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()

            try:
                product_data = data.pop("products", [])
                if not isinstance(product_data[0], dict):
                    product_data = json.loads(product_data[0])
            except Exception as ex:
                print(ex)
                raise ValueError("There was an issue with products or with the attachments")

            delivery_address = AddressSerializer(
                data=(
                    data["delivery_address"]
                    if isinstance(data["delivery_address"], dict)
                    else json.loads(data["delivery_address"])
                )
            )
            delivery_address.is_valid(raise_exception=True)
            data["delivery_address"] = delivery_address.save().id

            serializer = self.serializer_class(data=data)

            serializer.is_valid(raise_exception=True)
            offer = serializer.save(user=request.user)
            offer.user = request.user
            offer.save()

            for product_info in product_data:
                OfferProduct.objects.create(**product_info, offer=offer)

            return Response(status=status.HTTP_200_OK)

        except Exception as ex:
            print(ex)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super().get_queryset().select_related("quote")  # Pre-fetch related quote

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

        return qs.none()


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


class RetrieveUpdateInvoiceViewSet(CheckQuoteManagerGroupMixin, ModelViewSet):
    serializer_class = QuoteOfferSerializer
    queryset = QuoteOffer.objects.all()
    http_method_names = ["get", "patch"]
    permission_classes = [
        IsAuthenticated,
    ]
