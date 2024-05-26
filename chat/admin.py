from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ChatMessage, Thread


@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    pass


@admin.register(Thread)
class ThreadAdmin(ModelAdmin):
    pass
