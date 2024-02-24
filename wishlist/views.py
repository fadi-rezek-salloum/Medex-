from django.shortcuts import get_object_or_404
from product.models import Product
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Wishlist
from .serializers import WishlistSerializer


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    queryset = Wishlist.objects.all()
    lookup_field = "sku"

    def list(self, request):
        queryset = self.queryset.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        try:
            product = get_object_or_404(Product, sku=request.data["sku"])
            self.queryset.get_or_create(user=request.user, product=product)[0]

            return Response(status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, sku=None):
        wishlist = get_object_or_404(self.queryset, product__sku=sku, user=request.user)

        wishlist.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
