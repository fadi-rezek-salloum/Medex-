import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import ChatMessage, Thread

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for real-time chat.
    """

    async def connect(self):
        """
        Handles a new WebSocket connection.
        """
        self.other_user = self.scope["url_route"]["kwargs"]["other_user"]
        self.me = await self.get_user(self.scope["url_route"]["kwargs"]["user"])

        self.thread_obj = await self.get_thread(self.me, self.other_user)

        self.chat_room = f"thread_{self.thread_obj.id}"
        await self.channel_layer.group_add(self.chat_room, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        """
        await self.channel_layer.group_discard(self.chat_room, self.channel_name)

    async def receive(self, text_data):
        """
        Handles receiving messages from WebSocket.
        """
        data = json.loads(text_data)
        message = data.get("message")

        chat_message = await self.create_chat_message(message)
        message_data = {
            "message_id": str(chat_message.id),
            "message": chat_message.message,
            "user_id": str(self.me.id),
            "profile_pic": await self.get_user_profile_picture(self.me),
        }

        await self.channel_layer.group_send(
            self.chat_room, {"type": "chat_message", "message_data": message_data}
        )

    async def chat_message(self, event):
        """
        Sends chat message to WebSocket clients.
        """
        message_data = event["message_data"]

        await self.send(
            text_data=json.dumps(
                {
                    "message_id": message_data["message_id"],
                    "message": message_data["message"],
                    "user_id": message_data["user_id"],
                    "profile_pic": message_data["profile_pic"],
                }
            )
        )

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Retrieves a user asynchronously from the database.
        """
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_thread(self, user, other_id):
        """
        Retrieves a chat thread asynchronously from the database.
        """
        return Thread.objects.get_or_new(user, other_id)[0]

    @database_sync_to_async
    def create_chat_message(self, msg):
        """
        Creates a chat message asynchronously and saves it to the database.
        """
        return ChatMessage.objects.create(thread=self.thread_obj, user=self.me, message=msg)

    @database_sync_to_async
    def get_user_profile_picture(self, user):
        """
        Retrieves the profile picture URL for a user asynchronously.
        """
        if user.parent:
            profile_picture = (
                user.parent.buyer_profile.profile_picture
                if user.parent.is_buyer
                else user.parent.supplier_profile.profile_picture
            )
        else:
            profile_picture = (
                user.buyer_profile.profile_picture
                if user.is_buyer
                else user.supplier_profile.profile_picture
            )

        return profile_picture.url if profile_picture else None
