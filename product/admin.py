from django.contrib import admin

from .models import Brand, Category, PrivateCategory, Product

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(PrivateCategory)
