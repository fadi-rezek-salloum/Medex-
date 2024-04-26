from django.urls import path

from . import views

app_name = "quote"

urlpatterns = [
    path("", views.ListCreateQuoteView.as_view()),
    path("offer/", views.ListCreateQuoteOfferView.as_view()),
    path("offer/<id>/", views.RetrieveQuoteOfferView.as_view()),
    path("invoices/", views.RetrieveUpdateInvoiceView.as_view()),
    path("invoices/<pk>/", views.RetrieveUpdateInvoiceView.as_view()),
]
