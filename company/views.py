from account.serializers import AddressSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
from product.models import PrivateCategory
from product.serializers import PrivateCategorySerializer
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response

from .mixins import CheckAdminGroupMixin
from .models import Company
from .serializers import CompanySerializer

User = get_user_model()


class CompanyView(CheckAdminGroupMixin, RetrieveUpdateAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def get_object(self):
        user_id = self.kwargs.get("id")
        user = User.objects.filter(id=user_id).first()
        if user:
            return Company.objects.filter(Q(user=user) | Q(user=user.parent)).first()
        return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        company_serializer = self.get_serializer(instance, context={"request": request})

        data = {"company": company_serializer.data}

        if instance.user.is_supplier:
            user_products = PrivateCategory.objects.filter(supplier=instance.user)
            products_serializer = PrivateCategorySerializer(
                user_products, many=True, context={"request": request}
            )
            data["products"] = products_serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance and request.user.is_authenticated:
            data = request.data.copy()

            address_data = data.pop("address", None)
            if address_data:
                address_serializer = AddressSerializer(data=address_data)
                address_serializer.is_valid(raise_exception=True)
                address_instance = address_serializer.save()
                instance.address = address_instance
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance and request.user.is_authenticated:
            data = request.data
            profile_picture = data.get("profile_picture")
            delete_profile_picture = data.get("delete_profile_picture")
            cover_picture = data.get("cover_picture")
            delete_cover_picture = data.get("delete_cover_picture")

            if profile_picture:
                instance.company_profile_picture = profile_picture
            elif delete_profile_picture:
                instance.company_profile_picture.delete()
            elif cover_picture:
                instance.company_cover_picture = cover_picture
            elif delete_cover_picture:
                instance.company_cover_picture.delete()

            instance.save()

            return Response(status=status.HTTP_200_OK)

        return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)
