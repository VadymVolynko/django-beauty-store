from django.shortcuts import render

from catalog.models import Product


def home_view(request):
    products = Product.objects.filter(is_available=True)[:6]

    context = {
        "products": products,
    }

    return render(request, "catalog/home.html", context)
