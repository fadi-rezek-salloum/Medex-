from django.urls import path

from . import views

app_name = "wallet"

urlpatterns = [
    path("", views.WalletRetrieveAPIView.as_view()),
    path("withdraw/", views.WithdrawAPIView.as_view()),
]
