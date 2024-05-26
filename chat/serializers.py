from account.serializers import UserSerializer
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.timesince import timesince
from rest_framework import serializers

from .models import ChatMessage, Thread


class ThreadSerializer(serializers.ModelSerializer):
    first = serializers.SerializerMethodField()
    second = serializers.SerializerMethodField()
    room_group_name = serializers.CharField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = "__all__"

    def get_first(self, instance):
        return UserSerializer(instance.first).data

    def get_second(self, instance):
        return UserSerializer(instance.second).data

    def get_last_message(self, instance):
        last_message = instance.get_last_message

        if last_message:
            return {
                "message": Truncator(last_message.message).chars(25, html=True),
                "created": timesince(last_message.created, timezone.now()),
            }


class ChatMessageSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = "__all__"

    def get_user(self, instance):
        return UserSerializer(instance.user).data

    def get_created(self, instance):
        return timesince(instance.created, timezone.now())
