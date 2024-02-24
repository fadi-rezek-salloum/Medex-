from django.contrib import admin

from .models import QuoteAttachment, QuoteOffer, QuoteRequest

admin.site.register(QuoteRequest)
admin.site.register(QuoteOffer)
admin.site.register(QuoteAttachment)
