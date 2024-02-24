from decouple import config

from .base import *

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DATABASE_URL").split("/")[-1],
        "USER": config("DATABASE_URL").split("//")[1].split(":")[0],
        "PASSWORD": config("DATABASE_URL").split(":")[2].split("@")[0],
        "HOST": config("DATABASE_URL").split("@")[1].split(":")[0],
        "PORT": config("DATABASE_URL").split(":")[-1],
    }
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
