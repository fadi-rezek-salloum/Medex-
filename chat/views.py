from django.contrib.auth.models import AnonymousUser
from django.db.models import Case, IntegerField, Sum, When
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .mixins import CheckChatManagerGroupMixin
from .models import ChatMessage, Thread
from .serializers import ChatMessageSerializer, ThreadSerializer


class ChatInboxView(CheckChatManagerGroupMixin, generics.ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.parent if self.request.user.parent else self.request.user
        return Thread.objects.by_user(user)


class ChatThreadView(CheckChatManagerGroupMixin, generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        other_user_id = self.kwargs.get("id")
        user = self.request.user.parent if self.request.user.parent else self.request.user

        thread, created = Thread.objects.get_or_new(user, other_user_id)

        if thread is None:
            raise Http404("Thread not found")

        if not created:
            # Mark messages as read if the thread already existed
            ChatMessage.objects.filter(thread=thread, user=other_user_id, is_read=False).update(
                is_read=True
            )

        return ChatMessage.objects.filter(thread=thread)


class UnreadMessagesCountView(CheckChatManagerGroupMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            # If the user is not authenticated, return a response indicating authentication is required
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user.parent if request.user.parent else request.user

        unread_count = Thread.objects.by_user(user).aggregate(
            total_unread=Sum(
                Case(
                    When(chatmessage__is_read=False, chatmessage__user=user, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            )
        )["total_unread"]

        return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
