from django.contrib import admin

from .models import Order, OrderItem, ReturnRequest, ReturnRequestFile

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ReturnRequest)
admin.site.register(ReturnRequestFile)
