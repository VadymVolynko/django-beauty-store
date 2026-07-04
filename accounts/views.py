from hmac import compare_digest

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from decouple import config

from accounts.decorators import OWNER_SESSION_KEY, owner_required
from accounts.forms import RegisterForm
from accounts.models import EmailVerificationToken, User
from booking.models import Appointment
from catalog.models import Product
from orders.models import Order, OrderItem

OWNER_LOGIN = config("OWNER_LOGIN", default="")
OWNER_PASSWORD = config("OWNER_PASSWORD", default="")
OWNER_PASSWORD_ALIASES = [
    password.strip()
    for password in config("OWNER_PASSWORD_ALIASES", default="").split(",")
    if password.strip()
]
OWNER_LOGIN_FAILURES_SESSION_KEY = "owner_login_failures"
OWNER_LOGIN_LOCKED_UNTIL_SESSION_KEY = "owner_login_locked_until"
OWNER_LOGIN_MAX_FAILURES = 5
OWNER_LOGIN_LOCK_SECONDS = 15 * 60


def _valid_owner_passwords():
    passwords = [OWNER_PASSWORD.strip(), *OWNER_PASSWORD_ALIASES]
    return [password for password in passwords if password]


def _owner_credentials_match(identifier, password):
    owner_login = OWNER_LOGIN.strip().lower()
    if not owner_login or not identifier:
        return False
    if identifier.strip().lower() != owner_login:
        return False
    return any(compare_digest(password.strip(), valid) for valid in _valid_owner_passwords())


def _owner_login_is_locked(request):
    locked_until = request.session.get(OWNER_LOGIN_LOCKED_UNTIL_SESSION_KEY)
    if not locked_until:
        return False
    try:
        locked_until = timezone.datetime.fromisoformat(locked_until)
    except ValueError:
        request.session.pop(OWNER_LOGIN_LOCKED_UNTIL_SESSION_KEY, None)
        request.session.modified = True
        return False
    if timezone.is_naive(locked_until):
        locked_until = timezone.make_aware(locked_until)
    if timezone.now() < locked_until:
        return True
    request.session.pop(OWNER_LOGIN_LOCKED_UNTIL_SESSION_KEY, None)
    request.session[OWNER_LOGIN_FAILURES_SESSION_KEY] = 0
    request.session.modified = True
    return False


def _record_owner_login_failure(request):
    failures = request.session.get(OWNER_LOGIN_FAILURES_SESSION_KEY, 0) + 1
    request.session[OWNER_LOGIN_FAILURES_SESSION_KEY] = failures
    if failures >= OWNER_LOGIN_MAX_FAILURES:
        locked_until = timezone.now() + timezone.timedelta(seconds=OWNER_LOGIN_LOCK_SECONDS)
        request.session[OWNER_LOGIN_LOCKED_UNTIL_SESSION_KEY] = locked_until.isoformat()
    request.session.modified = True


def _clear_owner_login_failures(request):
    request.session.pop(OWNER_LOGIN_FAILURES_SESSION_KEY, None)
    request.session.pop(OWNER_LOGIN_LOCKED_UNTIL_SESSION_KEY, None)
    request.session.modified = True


def _enable_owner_session(request):
    logout(request)
    _clear_owner_login_failures(request)
    request.session[OWNER_SESSION_KEY] = True
    request.session.set_expiry(60 * 60 * 4)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        first_name = form.cleaned_data.get("first_name", "")
        last_name = form.cleaned_data.get("last_name", "")
        phone_number = form.cleaned_data.get("phone_number", "")

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
            phone_number=phone_number,
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
            subject=_("Verify your Beauty Store account"),
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

        if email == OWNER_LOGIN.strip().lower():
            if _owner_login_is_locked(request):
                error = _("Too many owner login attempts. Please try again later.")
                return render(request, "accounts/auth.html", {"tab": "login", "error": error})
            if _owner_credentials_match(email, password):
                _enable_owner_session(request)
                messages.success(request, _("Owner access enabled."))
                return redirect("owner-dashboard")
            _record_owner_login_failure(request)
            error = _("Invalid owner credentials.")
            return render(request, "accounts/auth.html", {"tab": "login", "error": error})

        if _owner_credentials_match(email, password):
            _enable_owner_session(request)
            messages.success(request, _("Owner access enabled."))
            return redirect("owner-dashboard")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            name = user.first_name or user.username
            messages.success(request, _("Welcome back, %(name)s!") % {"name": name})
            return redirect(request.GET.get("next", "home"))
        elif settings.DEBUG and settings.ENABLE_DEMO_LOGIN and email and password:
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
            messages.success(request, _("Demo login active. Welcome to the portfolio preview."))
            return redirect(request.GET.get("next", "home"))
        else:
            try:
                u = User.objects.get(email__iexact=email)
                if not u.is_active:
                    error = _("Please verify your email first. Check your inbox.")
                else:
                    error = _("Invalid email or password.")
            except User.DoesNotExist:
                error = _("Invalid email or password.")

    return render(request, "accounts/auth.html", {"tab": "login", "error": error})


def verify_email_view(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)

    if token_obj.is_expired():
        user = token_obj.user
        token_obj.delete()
        user.delete()
        messages.error(request, _("Verification link has expired. Please register again."))
        return redirect("register")

    user = token_obj.user
    user.is_active = True
    user.save()
    token_obj.delete()

    login(request, user, backend="accounts.backends.EmailBackend")
    messages.success(
        request,
        _("Welcome to Beauty Store, %(name)s!") % {"name": user.first_name or user.username},
    )
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

        if _owner_login_is_locked(request):
            error = _("Too many owner login attempts. Please try again later.")
            return render(request, "accounts/owner_login.html", {"error": error})

        if _owner_credentials_match(username, password):
            _enable_owner_session(request)
            messages.success(request, _("Owner access enabled."))
            return redirect("owner-dashboard")
        _record_owner_login_failure(request)
        error = _("Wrong owner login or password.")

    return render(request, "accounts/owner_login.html", {"error": error})


@owner_required
def owner_dashboard_view(request):
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
    messages.success(request, _("Owner access closed."))
    return redirect("login")
