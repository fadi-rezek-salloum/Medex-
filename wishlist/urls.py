from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "product"

router = DefaultRouter()
router.register("", views.WishlistViewSet)

urlpatterns = [path("", include(router.urls))]
