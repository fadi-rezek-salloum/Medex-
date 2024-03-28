from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    pass
