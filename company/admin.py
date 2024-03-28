from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Company


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    pass
