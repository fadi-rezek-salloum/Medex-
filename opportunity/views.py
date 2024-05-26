import json

from account.serializers import AddressSerializer
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from taggit.models import Tag

from .mixins import CheckQuoteManagerGroupMixin
from .models import Opportunity
from .pagination import OpportunityPagination
from .serializers import OpportunitySerializer, TagSerializer


class OpportunityCreateView(CheckQuoteManagerGroupMixin, CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OpportunitySerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        target_suppliers = data.pop("target_suppliers", [])
        tags = data.pop("tags", [])
        address = data.pop("delivery_address")

        delivery_address = AddressSerializer(
            data=(address if isinstance(address, dict) else json.loads(address))
        )
        delivery_address.is_valid(raise_exception=True)
        address_obj = delivery_address.save()

        data["delivery_address"] = address_obj.id

        serializer = self.serializer_class(data=data)

        serializer.is_valid(raise_exception=True)

        opportunity = serializer.save(user=request.user)

        for supplier in target_suppliers:
            opportunity.target_suppliers.add(supplier)

        for tag in tags:
            opportunity.tags.add(tag)

        return Response(status=status.HTTP_201_CREATED)


class OpportunityListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = OpportunitySerializer
    queryset = Opportunity.objects.order_by("-created")
    pagination_class = OpportunityPagination


class OpportunityDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = OpportunitySerializer
    queryset = Opportunity.objects.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        obj.views = obj.views + 1
        obj.save()

        return super().get(request, *args, **kwargs)


class TagListView(ListAPIView):
    permission_classes = [
        AllowAny,
    ]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
