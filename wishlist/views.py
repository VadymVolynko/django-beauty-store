from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _

from catalog.models import Product
from wishlist.models import WishlistItem


def _safe_next(request, fallback_url_name):
    candidate = request.POST.get("next") or request.META.get("HTTP_REFERER", "")
    if candidate and url_has_allowed_host_and_scheme(
        candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return candidate
    return reverse(fallback_url_name)


@login_required
def wishlist_view(request):
    items = WishlistItem.objects.filter(user=request.user).select_related(
        "product__brand", "product__category"
    )
    page_obj = Paginator(items, 12).get_page(request.GET.get("page"))
    return render(request, "wishlist/wishlist.html", {"items": page_obj, "page_obj": page_obj})


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    messages.success(request, _('"%(name)s" added to wishlist.') % {"name": product.name})
    return redirect(_safe_next(request, "catalog"))


@login_required
def wishlist_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    messages.success(request, _('"%(name)s" removed from wishlist.') % {"name": product.name})
    return redirect(_safe_next(request, "wishlist"))
