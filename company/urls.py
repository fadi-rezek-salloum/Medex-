from django.urls import path

from . import views

app_name = "company"

urlpatterns = [path("<id>/", views.CompanyView.as_view())]
