import os

import dj_database_url
from decouple import config

from .base import *

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = []

DATABASES = {
    "default": dj_database_url.config(default="sqlite:///" + os.path.join("db.sqlite3"))
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True


# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3080",
#     "http://127.0.0.1:3000",
# ]
