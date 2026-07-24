from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts.views import owner_dashboard_view, owner_logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("catalog.urls")),
    path("accounts/", include("accounts.urls")),
    path("owner/", owner_dashboard_view, name="owner-dashboard"),
    path("owner/logout/", owner_logout_view, name="owner-logout"),
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
