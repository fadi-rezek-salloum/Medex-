from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.ChatInboxView.as_view(), name="inbox"),
    path("<str:id>/", views.ChatThreadView.as_view(), name="thread"),
    path("<str:id>/count/", views.UnreadMessagesCountView.as_view(), name="unread-count"),
]
