from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(ModelAdmin):
    pass
