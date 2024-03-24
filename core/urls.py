from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/account/", include("account.urls", namespace="account")),
    path("api/product/", include("product.urls", namespace="product")),
    path("api/contact/", include("contact.urls", namespace="contact")),
    path("api/quote/", include("quote.urls", namespace="quote")),
    path("api/wishlist/", include("wishlist.urls", namespace="wishlist")),
    path("api/order/", include("order.urls", namespace="order")),
    path("api/chat/", include("chat.urls", namespace="chat")),
    path("api/stats/", include("stats.urls", namespace="stats")),
    path("api/company/", include("company.urls", namespace="company")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
