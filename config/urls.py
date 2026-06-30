from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("catalog.urls")),
    path("accounts/", include("accounts.urls")),
    path("booking/", include("booking.urls")),
    path("", include("cart.urls")),
    path("", include("orders.urls")),
    path("", include("wishlist.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
