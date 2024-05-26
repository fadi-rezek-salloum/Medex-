from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import OfferProduct, QuoteAttachment, QuoteOffer, QuoteProduct, QuoteRequest


@admin.register(QuoteRequest)
class QuoteRequestAdmin(ModelAdmin):
    pass


@admin.register(QuoteOffer)
class QuoteOfferAdmin(ModelAdmin):
    pass


@admin.register(QuoteAttachment)
class QuoteAttachmentAdmin(ModelAdmin):
    pass


@admin.register(QuoteProduct)
class QuoteProductAdmin(ModelAdmin):
    pass


@admin.register(OfferProduct)
class OfferProductAdmin(ModelAdmin):
    pass
