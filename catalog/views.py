from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Brand, Category, Product
from reviews.forms import ReviewForm


def home_view(request):
    products = Product.objects.filter(is_available=True).select_related("brand")[:6]
    return render(request, "catalog/home.html", {"products": products})


def catalog_view(request):
    products = Product.objects.filter(is_available=True).select_related("category", "brand")
    categories = Category.objects.all()
    brands = Brand.objects.all()

    category_slug = request.GET.get("category")
    brand_slug = request.GET.get("brand")
    query = request.GET.get("q", "").strip()

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if query:
        products = products.filter(name__icontains=query)

    context = {
        "products": products,
        "categories": categories,
        "brands": brands,
        "selected_category": category_slug,
        "selected_brand": brand_slug,
        "query": query,
    }
    return render(request, "catalog/catalog.html", context)


def product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.select_related("user")

    user_review = None
    review_form = None

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        if not user_review:
            review_form = ReviewForm(request.POST or None)
            if request.method == "POST" and review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Your review has been posted.")
                return redirect("product", slug=slug)

    return render(request, "catalog/product.html", {
        "product": product,
        "reviews": reviews,
        "review_form": review_form,
        "user_review": user_review,
    })

