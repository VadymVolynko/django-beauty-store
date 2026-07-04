from decimal import Decimal
from secrets import token_urlsafe

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from cart.cart import Cart
from catalog.models import Product
from orders.forms import CheckoutForm
from orders.models import Order, OrderItem

RECENT_ORDER_IDS_SESSION_KEY = "recent_order_ids"
CHECKOUT_TOKEN_SESSION_KEY = "checkout_token"
COMPLETED_CHECKOUTS_SESSION_KEY = "completed_checkout_orders"


def _remember_recent_order(request, order):
    order_ids = request.session.get(RECENT_ORDER_IDS_SESSION_KEY, [])
    order_ids = [order_id for order_id in order_ids if order_id != order.pk]
    order_ids.append(order.pk)
    request.session[RECENT_ORDER_IDS_SESSION_KEY] = order_ids[-5:]
    request.session.modified = True


def _can_view_order_success(request, order):
    if request.user.is_authenticated and order.user_id == request.user.id:
        return True
    return order.pk in request.session.get(RECENT_ORDER_IDS_SESSION_KEY, [])


def _get_checkout_token(request):
    checkout_token = request.session.get(CHECKOUT_TOKEN_SESSION_KEY)
    if not checkout_token:
        checkout_token = token_urlsafe(32)
        request.session[CHECKOUT_TOKEN_SESSION_KEY] = checkout_token
        request.session.modified = True
    return checkout_token


def _reset_checkout_token(request):
    request.session[CHECKOUT_TOKEN_SESSION_KEY] = token_urlsafe(32)
    request.session.modified = True


def _remember_completed_checkout(request, checkout_token, order):
    completed = request.session.get(COMPLETED_CHECKOUTS_SESSION_KEY, {})
    completed[checkout_token] = order.pk
    request.session[COMPLETED_CHECKOUTS_SESSION_KEY] = dict(list(completed.items())[-5:])
    request.session.modified = True


def _completed_order_for_token(request, checkout_token):
    completed = request.session.get(COMPLETED_CHECKOUTS_SESSION_KEY, {})
    order_id = completed.get(checkout_token)
    if not order_id:
        return None
    return Order.objects.filter(pk=order_id).first()


def _cart_items_with_locked_products(cart):
    items = list(cart)
    products = Product.objects.select_for_update().in_bulk(
        [item["id"] for item in items]
    )
    enriched_items = []

    for item in items:
        product = products.get(item["id"])
        if product is None:
            raise ValueError(_("A product in your cart is no longer available."))
        if not product.is_available:
            raise ValueError(_("%(name)s is currently unavailable.") % {"name": product.name})
        if item["quantity"] > product.stock:
            raise ValueError(
                _("%(name)s has only %(stock)s item(s) left in stock.")
                % {"name": product.name, "stock": product.stock}
            )
        enriched_items.append((item, product))

    return enriched_items


def checkout_view(request):
    cart = Cart(request)
    submitted_token = request.POST.get("checkout_token", "")

    if len(cart) == 0:
        completed_order = _completed_order_for_token(request, submitted_token)
        if completed_order is not None:
            return redirect("order-success", pk=completed_order.pk)
        return redirect("cart")

    initial = {}
    if request.user.is_authenticated:
        initial = {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }

    form = CheckoutForm(request.POST or None, initial=initial)
    checkout_token = _get_checkout_token(request)

    if request.method == "POST" and form.is_valid():
        completed_order = _completed_order_for_token(request, submitted_token)
        if completed_order is not None:
            return redirect("order-success", pk=completed_order.pk)
        if not submitted_token or submitted_token != checkout_token:
            messages.error(
                request,
                _("This checkout session has expired. Please review your cart and try again."),
            )
            return redirect("checkout")

        try:
            with transaction.atomic():
                enriched_items = _cart_items_with_locked_products(cart)
                total_price = sum(
                    (product.price * item["quantity"] for item, product in enriched_items),
                    Decimal("0.00"),
                )
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    email=form.cleaned_data["email"],
                    phone=form.cleaned_data["phone"],
                    address=form.cleaned_data["address"],
                    city=form.cleaned_data["city"],
                    postal_code=form.cleaned_data["postal_code"],
                    status=Order.Status.PENDING,
                    total_price=total_price,
                )

                for item, product in enriched_items:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        name=product.name,
                        price=product.price,
                        quantity=item["quantity"],
                    )
                    product.stock -= item["quantity"]
                    if product.stock == 0:
                        product.is_available = False
                    product.save(update_fields=["stock", "is_available", "updated_at"])
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("cart")

        _remember_completed_checkout(request, submitted_token, order)
        _reset_checkout_token(request)
        cart.clear()
        _remember_recent_order(request, order)

        body = render_to_string("orders/email_confirmation.txt", {"order": order})
        send_mail(
            subject=_("Order #%(number)s confirmed - Beauty Store") % {"number": order.pk},
            message=body,
            from_email=None,
            recipient_list=[order.email],
            fail_silently=True,
        )

        return redirect("order-success", pk=order.pk)

    return render(
        request,
        "orders/checkout.html",
        {"form": form, "cart": cart, "checkout_token": checkout_token},
    )


def order_success_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not _can_view_order_success(request, order):
        raise Http404
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    page_obj = Paginator(orders, 10).get_page(request.GET.get("page"))
    return render(request, "orders/order_history.html", {"orders": page_obj, "page_obj": page_obj})
