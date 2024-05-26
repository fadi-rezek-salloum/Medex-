from django.urls import path

from . import views

app_name = "opportunity"

urlpatterns = [
    path("", views.OpportunityListView.as_view()),
    path("create/", views.OpportunityCreateView.as_view()),
    path("tags/", views.TagListView.as_view()),
    path("<pk>/", views.OpportunityDetailView.as_view()),
]
