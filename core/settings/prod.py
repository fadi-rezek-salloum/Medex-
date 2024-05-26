import dj_database_url
from decouple import config

from .base import *

ALLOWED_HOSTS = ["medex2b.com"]
CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS

DATABASES = {"default": dj_database_url.config(default=config("DATABASE_URL"))}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

CORS_ALLOWED_ORIGINS = [
    "https://medex2b.com",
]

DEBUG = False
