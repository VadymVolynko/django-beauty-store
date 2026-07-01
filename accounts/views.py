from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from decouple import config

from accounts.forms import RegisterForm
from accounts.models import EmailVerificationToken
from booking.models import Appointment
from catalog.models import Product
from orders.models import Order, OrderItem

OWNER_SESSION_KEY = "owner_access"
OWNER_LOGIN = config("OWNER_LOGIN", default="")
OWNER_PASSWORD = config("OWNER_PASSWORD", default="")
OWNER_PASSWORD_ALIASES = [
    password.strip()
    for password in config("OWNER_PASSWORD_ALIASES", default="").split(",")
    if password.strip()
]


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        first_name = form.cleaned_data.get("first_name", "")
        last_name = form.cleaned_data.get("last_name", "")

        # Auto-generate a unique username from email prefix
        base = email.split("@")[0][:28]
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )

        token_obj = EmailVerificationToken.objects.create(user=user)
        verify_url = request.build_absolute_uri(
            reverse("verify-email", args=[token_obj.token])
        )

        body = render_to_string("accounts/email_verify.txt", {
            "user": user,
            "verify_url": verify_url,
        })
        send_mail(
            subject="Verify your Beauty Store account",
            message=body,
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return render(request, "accounts/check_email.html", {"email": email})

    return render(request, "accounts/auth.html", {"tab": "register", "form": form})


def login_view(request):
    if request.user.is_authenticated and request.method != "POST":
        return redirect("home")

    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        owner_login = OWNER_LOGIN.strip().lower()
        owner_password = OWNER_PASSWORD.strip()

        valid_owner_passwords = {owner_password, *OWNER_PASSWORD_ALIASES}

        if email == owner_login and password.strip() in valid_owner_passwords:
            logout(request)
            request.session[OWNER_SESSION_KEY] = True
            request.session.set_expiry(60 * 60 * 4)
            messages.success(request, "Owner access enabled.")
            return redirect("owner-dashboard")
        if email == owner_login:
            error = "Invalid owner password."
            return render(request, "accounts/auth.html", {"tab": "login", "error": error})

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            name = user.first_name or user.username
            messages.success(request, f"Welcome back, {name}!")
            return redirect(request.GET.get("next", "home"))
        elif settings.DEBUG and email and password:
            user = User.objects.filter(email__iexact=email).first()
            if user is None:
                base = (email.split("@")[0] or "demo")[:24]
                username = base
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base}{counter}"
                    counter += 1
                user = User.objects.create(
                    username=username,
                    email=email.lower(),
                    first_name="Demo",
                    last_name="User",
                    is_active=True,
                )
                user.set_unusable_password()
                user.save()
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
            login(request, user, backend="accounts.backends.EmailBackend")
            messages.success(request, "Demo login active. Welcome to the portfolio preview.")
            return redirect(request.GET.get("next", "home"))
        else:
            try:
                u = User.objects.get(email__iexact=email)
                if not u.is_active:
                    error = "Please verify your email first. Check your inbox."
                else:
                    error = "Invalid email or password."
            except User.DoesNotExist:
                error = "Invalid email or password."

    return render(request, "accounts/auth.html", {"tab": "login", "error": error})


def verify_email_view(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)

    if token_obj.is_expired():
        user = token_obj.user
        token_obj.delete()
        user.delete()
        messages.error(request, "Verification link has expired. Please register again.")
        return redirect("register")

    user = token_obj.user
    user.is_active = True
    user.save()
    token_obj.delete()

    login(request, user, backend="accounts.backends.EmailBackend")
    messages.success(request, f"Welcome to Beauty Store, {user.first_name or user.username}!")
    return redirect("home")


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


def owner_login_view(request):
    if request.session.get(OWNER_SESSION_KEY):
        return redirect("owner-dashboard")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if username == OWNER_LOGIN and password == OWNER_PASSWORD:
            request.session[OWNER_SESSION_KEY] = True
            request.session.set_expiry(60 * 60 * 4)
            messages.success(request, "Owner access enabled.")
            return redirect("owner-dashboard")
        error = "Wrong owner login or password."

    return render(request, "accounts/owner_login.html", {"error": error})


def owner_dashboard_view(request):
    if not request.session.get(OWNER_SESSION_KEY):
        return redirect("login")

    orders = Order.objects.select_related("user").prefetch_related("items")[:20]
    appointments = Appointment.objects.select_related(
        "user", "specialist", "service"
    )[:20]
    top_items = (
        OrderItem.objects.values("name")
        .annotate(quantity=Sum("quantity"), orders=Count("order", distinct=True))
        .order_by("-quantity")[:8]
    )

    context = {
        "orders": orders,
        "appointments": appointments,
        "top_items": top_items,
        "total_orders": Order.objects.count(),
        "total_revenue": Order.objects.aggregate(total=Sum("total_price"))["total"] or 0,
        "total_appointments": Appointment.objects.count(),
        "pending_appointments": Appointment.objects.filter(
            status=Appointment.Status.PENDING
        ).count(),
        "total_products": Product.objects.count(),
        "items_sold": OrderItem.objects.aggregate(total=Sum("quantity"))["total"] or 0,
    }
    return render(request, "accounts/owner_dashboard.html", context)


def owner_logout_view(request):
    request.session.pop(OWNER_SESSION_KEY, None)
    messages.success(request, "Owner access closed.")
    return redirect("login")
