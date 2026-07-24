from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.decorators import owner_required
from catalog.forms import ProductForm
from catalog.models import Brand, Category, Product
from reviews.forms import ReviewForm
from wishlist.models import WishlistItem


def home_view(request):
    if not request.user.is_authenticated and not request.session.get("owner_access"):
        return redirect("login")

    products = Product.objects.filter(is_available=True, is_featured=True).select_related("brand")[:6]
    if not products:
        products = Product.objects.filter(is_available=True).select_related("brand")[:6]
    return render(request, "catalog/home.html", {"products": products})


def catalog_view(request):
    brands = Brand.objects.all().order_by("name")
    page_obj = Paginator(brands, 12).get_page(request.GET.get("page"))
    return render(request, "catalog/brand_list.html", {"brands": page_obj, "page_obj": page_obj})


def brand_products_view(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(is_available=True, brand=brand).select_related("category").order_by("name")
    categories = Category.objects.filter(products__brand=brand).distinct()

    category_slug = request.GET.get("category")
    query = request.GET.get("q", "").strip()

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(name__icontains=query)

    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "brand": brand,
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_slug,
        "query": query,
    }
    return render(request, "catalog/brand_products.html", context)


def product_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.select_related("user")

    user_review = None
    review_form = None
    in_wishlist = False

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        if not user_review:
            review_form = ReviewForm(request.POST or None)
            if request.method == "POST" and review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, _("Your review has been posted."))
                return redirect("product", slug=slug)
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

    return render(request, "catalog/product.html", {
        "product": product,
        "reviews": reviews,
        "review_form": review_form,
        "user_review": user_review,
        "in_wishlist": in_wishlist,
    })


@method_decorator(owner_required, name="dispatch")
class ProductManageListView(ListView):
    model = Product
    template_name = "catalog/product_manage_list.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.select_related("category", "brand").order_by("-created_at")


@method_decorator(owner_required, name="dispatch")
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("owner-products")


@method_decorator(owner_required, name="dispatch")
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("owner-products")


@method_decorator(owner_required, name="dispatch")
class ProductDeleteView(DeleteView):
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("owner-products")
