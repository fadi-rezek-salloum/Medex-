from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import QuoteAttachment, QuoteOffer, QuoteRequest


@admin.register(QuoteRequest)
class QuoteRequestAdmin(ModelAdmin):
    pass


@admin.register(QuoteOffer)
class QuoteOfferAdmin(ModelAdmin):
    pass


@admin.register(QuoteAttachment)
class QuoteAttachmentAdmin(ModelAdmin):
    pass
