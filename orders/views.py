from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from cart.cart import Cart
from orders.forms import CheckoutForm
from orders.models import Order, OrderItem


def checkout_view(request):
    cart = Cart(request)

    if len(cart) == 0:
        return redirect("cart")

    initial = {}
    if request.user.is_authenticated:
        initial = {
            "email":      request.user.email,
            "first_name": request.user.first_name,
            "last_name":  request.user.last_name,
        }

    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        order = Order.objects.create(
            user        = request.user if request.user.is_authenticated else None,
            first_name  = form.cleaned_data["first_name"],
            last_name   = form.cleaned_data["last_name"],
            email       = form.cleaned_data["email"],
            phone       = form.cleaned_data["phone"],
            address     = form.cleaned_data["address"],
            city        = form.cleaned_data["city"],
            postal_code = form.cleaned_data["postal_code"],
            total_price = cart.total_price,
        )

        for item in cart:
            OrderItem.objects.create(
                order    = order,
                product  = None,
                name     = item["name"],
                price    = item["price"],
                quantity = item["quantity"],
            )

        cart.clear()

        body = render_to_string("orders/email_confirmation.txt", {"order": order})
        send_mail(
            subject=f"Order #{order.pk} confirmed — Beauty Store",
            message=body,
            from_email=None,
            recipient_list=[order.email],
            fail_silently=True,
        )

        return redirect("order-success", pk=order.pk)

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


def order_success_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "orders/order_history.html", {"orders": orders})
