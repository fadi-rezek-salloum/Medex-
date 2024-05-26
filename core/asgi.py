import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from chat.routers import ws_patterns
from django.core.asgi import get_asgi_application

from .settings import base

django.setup()


if base.DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.dev")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.prod")


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(ws_patterns))),
    }
)
