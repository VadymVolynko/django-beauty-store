from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import Cart
from catalog.models import Product


def cart_view(request):
    cart = Cart(request)
    return render(request, "cart/cart.html", {"cart": cart})


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(product, quantity)
    return redirect("cart")


def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect("cart")


def cart_update(request, product_id):
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    cart.update(product_id, quantity)
    return redirect("cart")
