from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(ModelAdmin):
    pass
