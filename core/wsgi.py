import os

from django.core.wsgi import get_wsgi_application

from .settings import base

if base.DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.dev")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.prod")

application = get_wsgi_application()
