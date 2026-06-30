from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from accounts.forms import RegisterForm
from accounts.models import EmailVerificationToken


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
    if request.user.is_authenticated:
        return redirect("home")

    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            name = user.first_name or user.username
            messages.success(request, f"Welcome back, {name}!")
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
