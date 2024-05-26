import json

import jwt
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from stats.models import Stats

from .mixins import CheckBuyerAdminGroupMixin, CheckSupplierAdminGroupMixin
from .models import BuyerProfile, SupplierProfile, User
from .serializers import (
    AddressSerializer,
    CustomTokenObtainPairSerializer,
    StatsSerializer,
    UserSerializer,
)
from .utils import send_activation_email


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RefreshBuyerActivationLink(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        pass

    def get_serializer_class(self):
        pass

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.data)
        token = RefreshToken.for_user(user).access_token

        send_activation_email(
            f"/account/buyer/activate?token={str(token)}",
            "emails/activate_email.html",
            _("Medex Account Activation"),
            user.email,
        )

        return Response(status=status.HTTP_200_OK)


class BuyerRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        data = self.request.data.copy()

        shipping_address = AddressSerializer(data=json.loads(data["shipping_address"]))
        shipping_address.is_valid(raise_exception=True)
        shipping_address_instance = shipping_address.save()

        profile_picture = data.pop("profile_picture")[0]

        user = serializer.save(
            shipping_address=shipping_address_instance,
            is_buyer=True,
            is_active=False,  # Users are inactive until they verify their email
        )
        user.set_password(data["password"])
        user.save()

        BuyerProfile.objects.create(user=user, profile_picture=profile_picture)

        token = RefreshToken.for_user(user).access_token

        send_activation_email(
            f"/account/buyer/activate?token={str(token)}",
            "emails/activate_email.html",
            _("Medex Account Activation"),
            data["email"],
        )

        return user


class SupplierRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        shipping_address = AddressSerializer(data=json.loads(data["shipping_address"]))
        shipping_address.is_valid(raise_exception=True)
        data["shipping_address"] = shipping_address.save().id

        profile_picture = data.pop("profile_picture")[0]

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            user.set_password(data["password"])
            user.save()

            SupplierProfile.objects.create(user=user, profile_picture=profile_picture)

            return Response(
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        pass

    def get_serializer_class(self):
        pass

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")

            user = User.objects.get(id=payload["user_id"])

            if not user.is_active:
                user.is_active = True
                user.save()

            return Response(
                {"success": _("Your account has been successfully activated!")},
                status=status.HTTP_200_OK,
            )

        except jwt.ExpiredSignatureError:
            return Response(
                {"error": _("Activation link expired!")}, status=status.HTTP_400_BAD_REQUEST
            )

        except jwt.exceptions.DecodeError:
            return Response({"error": _("Invalid token!")}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        pass

    def get_serializer_class(self):
        pass

    def post(self, request, *args, **kwargs):
        email = request.data["email"]

        try:
            user = User.objects.get(email__iexact=email)

            if user:
                token = RefreshToken.for_user(user).access_token

                send_activation_email(
                    f"/account/password/reset/confirm?token={token}",
                    "emails/reset_password.html",
                    _("Medex Account Password Reset"),
                    user.email,
                )

        except Exception:
            pass

        return Response(status=status.HTTP_200_OK)


class PasswordResetConfirmView(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        pass

    def get_serializer_class(self):
        pass

    def post(self, request, *args, **kwargs):
        token = request.GET.get("token")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")

            user = User.objects.get(id=payload["user_id"])

            user.set_password(request.data["password"])
            user.save()
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        user = self.request.user
        context = {}
        serializer_context = self.get_serializer_context()

        serializer = self.get_serializer(user, context=serializer_context)
        context.update(serializer.data)

        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()

        shipping_address = AddressSerializer(data=json.loads(data["shipping_address"]))
        shipping_address.is_valid(raise_exception=True)
        data["shipping_address"] = shipping_address.save().id

        serializer = self.get_serializer(instance=request.user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        if request.data.get("profile_picture"):
            profile = BuyerProfile.objects.get(user=request.user)
            profile.profile_picture = request.data["profile_picture"]
            profile.save()

            return Response(status=status.HTTP_200_OK)

        elif request.data.get("delete_profile_picture"):
            profile = BuyerProfile.objects.get(user=request.user)
            profile.profile_picture.delete()
            profile.save()

            return Response(status=status.HTTP_200_OK)
        else:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        if str(request.data["id"]) == str(request.user.id):
            super().delete(request, *args, **kwargs)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class GetProfileView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"


class ShowUserStatsView(APIView):
    def get(self, request, *args, **kwargs):
        stats = Stats.objects.first()
        return Response(data=StatsSerializer(instance=stats).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        stats = Stats.objects.first()
        stats.show = False if stats.show == True else True
        stats.save()
        return Response(status=status.HTTP_200_OK)


class SupplierListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(is_supplier=True)


class UpdatePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        pass

    def get_serializer_class(self):
        pass

    def put(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response({"error": "current"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_200_OK)


class SupplierEmployeeView(CheckSupplierAdminGroupMixin, ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(parent=self.request.user)

        return qs

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        position = json.loads(data.get("position"))

        data.pop("position")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        user.set_password(data["password"])
        user.parent = request.user
        user.is_active = True
        user.is_supplier = True
        user.shipping_address = request.user.shipping_address

        group_mappings = {
            "p_man": "Supplier Product Manager",
            "q_man": "Supplier Quote Manager",
            "s_man": "Supplier Sale Manager",
            "c_man": "Supplier Chat",
        }
        for i in position:
            group_name = group_mappings.get(i.get("value"))
            if group_name:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)

        user.save()

        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        try:
            employee_id = request.data.get("employee_id")

            employee = User.objects.get(id=employee_id)

            if employee.parent == request.user:
                employee.delete()

                return Response(status=status.HTTP_200_OK)
        except Exception:
            pass

        return Response(status=status.HTTP_401_UNAUTHORIZED)


class BuyerEmployeeView(CheckBuyerAdminGroupMixin, ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(parent=self.request.user)

        return qs

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        position = json.loads(data.get("position"))

        data.pop("position")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        user.set_password(data["password"])
        user.parent = request.user
        user.is_active = True
        user.is_buyer = True
        user.shipping_address = request.user.shipping_address

        group_mappings = {
            "p_man": "Buyer Product Manager",
            "q_man": "Buyer Quote Manager",
            "o_man": "Buyer Order Manager",
            "c_man": "Buyer Chat",
        }
        for i in position:
            group_name = group_mappings.get(i.get("value"))
            if group_name:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)

        user.save()

        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        try:
            employee_id = request.data.get("employee_id")

            employee = User.objects.get(id=employee_id)

            if employee.parent == request.user:
                employee.delete()

                return Response(status=status.HTTP_200_OK)
        except Exception:
            pass

        return Response(status=status.HTTP_401_UNAUTHORIZED)
