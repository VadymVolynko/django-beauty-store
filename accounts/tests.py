from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.decorators import OWNER_SESSION_KEY
from accounts.models import EmailVerificationToken, User
from booking.models import Appointment, Service, Specialist
from orders.models import Order, OrderItem


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class AccountViewTests(TestCase):
    def test_register_creates_inactive_user_and_verification_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "phone_number": "+380501112233",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email="ada@example.com")
        self.assertFalse(user.is_active)
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ada@example.com", mail.outbox[0].to)

    @override_settings(DEBUG=True, ENABLE_DEMO_LOGIN=True)
    def test_debug_demo_login_creates_active_user(self):
        response = self.client.post(
            reverse("login"),
            {"email": "demo@example.com", "password": "anything"},
        )

        self.assertRedirects(response, reverse("home"))
        user = User.objects.get(email="demo@example.com")
        self.assertTrue(user.is_active)
        self.assertEqual(user.first_name, "Demo")

    def test_owner_login_sets_owner_session_flag(self):
        with patch("accounts.views.OWNER_LOGIN", "owner@example.com"), patch(
            "accounts.views.OWNER_PASSWORD", "secret"
        ):
            response = self.client.post(
                reverse("login"),
                {"email": "owner@example.com", "password": "secret"},
            )

        self.assertRedirects(response, reverse("owner-dashboard"))
        self.assertTrue(self.client.session[OWNER_SESSION_KEY])

    def test_empty_owner_password_does_not_enable_owner_access(self):
        with patch("accounts.views.OWNER_LOGIN", "owner@example.com"), patch(
            "accounts.views.OWNER_PASSWORD", ""
        ):
            response = self.client.post(
                reverse("login"),
                {"email": "owner@example.com", "password": ""},
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get(OWNER_SESSION_KEY, False))

    def test_owner_login_locks_after_repeated_failures(self):
        with patch("accounts.views.OWNER_LOGIN", "owner@example.com"), patch(
            "accounts.views.OWNER_PASSWORD", "secret"
        ):
            for _ in range(5):
                self.client.post(
                    reverse("login"),
                    {"email": "owner@example.com", "password": "wrong"},
                )
            response = self.client.post(
                reverse("login"),
                {"email": "owner@example.com", "password": "secret"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get(OWNER_SESSION_KEY, False))

    @override_settings(DEBUG=True, ENABLE_DEMO_LOGIN=False)
    def test_demo_login_can_be_disabled(self):
        response = self.client.post(
            reverse("login"),
            {"email": "demo-disabled@example.com", "password": "anything"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="demo-disabled@example.com").exists())

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse("profile"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_owner_dashboard_redirects_without_owner_session(self):
        response = self.client.get(reverse("owner-dashboard"))

        self.assertRedirects(response, reverse("login"))

    def test_owner_dashboard_shows_store_stats_with_owner_session(self):
        session = self.client.session
        session[OWNER_SESSION_KEY] = True
        session.save()

        user = User.objects.create_user(
            username="shopper", email="shopper@example.com", password="pass"
        )
        order = Order.objects.create(
            user=user,
            first_name="Ada",
            last_name="Lovelace",
            email="shopper@example.com",
            phone="+380501112233",
            address="1 Main St",
            city="Kyiv",
            postal_code="01001",
            status=Order.Status.PENDING,
            total_price="45.00",
        )
        OrderItem.objects.create(order=order, name="Serum", price="45.00", quantity=1)

        specialist = Specialist.objects.create(name="Kate", bio="Skincare pro", experience=3)
        service = Service.objects.create(
            name="Consultation", description="A skincare consult.", price="30.00", duration=30
        )
        Appointment.objects.create(
            user=user,
            specialist=specialist,
            service=service,
            date="2026-08-01",
            time="10:00",
            status=Appointment.Status.PENDING,
        )

        response = self.client.get(reverse("owner-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_orders"], 1)
        self.assertEqual(response.context["total_appointments"], 1)
        self.assertEqual(response.context["pending_appointments"], 1)
        self.assertIn(order, response.context["orders"])

    def test_owner_logout_clears_owner_session(self):
        session = self.client.session
        session[OWNER_SESSION_KEY] = True
        session.save()

        response = self.client.get(reverse("owner-logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertFalse(self.client.session.get(OWNER_SESSION_KEY, False))

# Create your tests here.
