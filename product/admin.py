from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Brand, Category, PrivateCategory, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    pass


@admin.register(PrivateCategory)
class PrivateCategoryAdmin(ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass
