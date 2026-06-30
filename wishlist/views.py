from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product
from wishlist.models import WishlistItem


@login_required
def wishlist_view(request):
    items = WishlistItem.objects.filter(user=request.user).select_related(
        "product__brand", "product__category"
    )
    return render(request, "wishlist/wishlist.html", {"items": items})


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f'"{product.name}" added to wishlist.')
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER", "catalog")
    return redirect(next_url)


@login_required
def wishlist_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'"{product.name}" removed from wishlist.')
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER", "wishlist")
    return redirect(next_url)
