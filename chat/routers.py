from django.urls import path

from .consumers import ChatConsumer

ws_patterns = [
    path("ws/chat/<other_user>/<user>/", ChatConsumer.as_asgi()),
]
