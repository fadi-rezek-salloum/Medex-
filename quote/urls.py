from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "quote"

router = DefaultRouter()

router.register(r"invoices", views.RetrieveUpdateInvoiceViewSet, basename="invoice")

urlpatterns = [
    path("", views.ListCreateQuoteView.as_view()),
    path("offer/", views.ListCreateQuoteOfferView.as_view()),
    path("offer/<id>/", views.RetrieveQuoteOfferView.as_view()),
] + router.urls
