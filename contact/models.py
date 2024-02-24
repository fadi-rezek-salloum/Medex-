from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    name = models.CharField(_("User Name"), max_length=255)
    email = models.EmailField(_("Email"), max_length=255)
    message = models.TextField(_("Message"))

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} -> {self.created}"
