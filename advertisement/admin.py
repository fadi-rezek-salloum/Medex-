from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(ModelAdmin):
    pass
