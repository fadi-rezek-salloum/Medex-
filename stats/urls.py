from django.urls import path

from . import views

app_name = "stats"

urlpatterns = [
    path("buyer/", views.BuyerStatsView.as_view()),
    path("supplier/", views.SupplierStatsView.as_view()),
]
