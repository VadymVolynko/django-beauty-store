import re

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
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

# Django's static() helper is a no-op unless DEBUG=True. This project has no
# S3/CDN, so media (product/specialist images) must be served by Django
# itself even in production on Render.
urlpatterns += [
    re_path(
        r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")),
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
