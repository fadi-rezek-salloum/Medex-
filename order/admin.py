from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Order, OrderItem, ReturnRequest, ReturnRequestFile


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    pass


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    pass


@admin.register(ReturnRequest)
class ReturnRequestAdmin(ModelAdmin):
    pass


@admin.register(ReturnRequestFile)
class ReturnRequestFileAdmin(ModelAdmin):
    pass
