from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from cart.cart import CART_SESSION_KEY
from catalog.models import Brand, Category, Product
from orders.models import Order, OrderItem


def create_product(**overrides):
    category = Category.objects.create(name="Cleansers", slug="cleansers")
    brand = Brand.objects.create(name="Pure Care", slug="pure-care")
    defaults = {
        "category": category,
        "brand": brand,
        "name": "Daily Cleanser",
        "slug": "daily-cleanser",
        "description": "Soft daily cleanser.",
        "price": "12.00",
        "stock": 20,
        "is_available": True,
    }
    defaults.update(overrides)
    return Product.objects.create(**defaults)


def checkout_payload(token):
    return {
        "checkout_token": token,
        "first_name": "Grace",
        "last_name": "Hopper",
        "email": "grace@example.com",
        "phone": "+380501112233",
        "address": "Main Street 1",
        "city": "Kyiv",
        "postal_code": "01001",
    }


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class CheckoutViewTests(TestCase):
    def get_checkout_token(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 200)
        return response.context["checkout_token"]

    def test_checkout_creates_order_items_reduces_stock_and_clears_cart(self):
        user = User.objects.create_user(
            username="buyer", email="buyer@example.com", password="pass"
        )
        product = create_product()
        self.client.force_login(user)
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "3"})
        token = self.get_checkout_token()

        response = self.client.post(reverse("checkout"), checkout_payload(token))

        order = Order.objects.get()
        product.refresh_from_db()
        self.assertRedirects(response, reverse("order-success", args=[order.pk]))
        self.assertEqual(order.user, user)
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.total_price, Decimal("36.00"))
        self.assertEqual(product.stock, 17)
        self.assertTrue(product.is_available)

        item = OrderItem.objects.get(order=order)
        self.assertEqual(item.product, product)
        self.assertEqual(item.name, product.name)
        self.assertEqual(item.price, product.price)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(self.client.session[CART_SESSION_KEY], {})

    def test_checkout_marks_product_unavailable_when_stock_reaches_zero(self):
        product = create_product(stock=2)
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "2"})
        token = self.get_checkout_token()

        self.client.post(reverse("checkout"), checkout_payload(token))

        product.refresh_from_db()
        self.assertEqual(product.stock, 0)
        self.assertFalse(product.is_available)

    def test_checkout_rejects_quantity_greater_than_stock(self):
        product = create_product(stock=1)
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "2"})
        token = self.get_checkout_token()

        response = self.client.post(reverse("checkout"), checkout_payload(token))

        product.refresh_from_db()
        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(product.stock, 1)

    def test_checkout_rejects_unavailable_product(self):
        product = create_product(is_available=False)
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "1"})
        token = self.get_checkout_token()

        response = self.client.post(reverse("checkout"), checkout_payload(token))

        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_duplicate_submit_returns_existing_order(self):
        product = create_product()
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "1"})
        token = self.get_checkout_token()

        first_response = self.client.post(reverse("checkout"), checkout_payload(token))
        second_response = self.client.post(reverse("checkout"), checkout_payload(token))

        order = Order.objects.get()
        self.assertRedirects(first_response, reverse("order-success", args=[order.pk]))
        self.assertRedirects(second_response, reverse("order-success", args=[order.pk]))
        self.assertEqual(Order.objects.count(), 1)

    def test_checkout_redirects_to_cart_when_cart_is_empty(self):
        response = self.client.get(reverse("checkout"))

        self.assertRedirects(response, reverse("cart"))

    def test_checkout_rejects_missing_token(self):
        product = create_product()
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "1"})
        self.get_checkout_token()
        payload = checkout_payload(token="")

        response = self.client.post(reverse("checkout"), payload)

        self.assertRedirects(response, reverse("checkout"))
        self.assertEqual(Order.objects.count(), 0)

    def test_order_success_allows_order_owner(self):
        user = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass"
        )
        order = Order.objects.create(
            user=user,
            first_name="Order",
            last_name="Owner",
            email="owner@example.com",
            phone="+380501112233",
            address="Main Street 1",
            city="Kyiv",
            postal_code="01001",
            total_price=Decimal("12.00"),
        )
        self.client.force_login(user)

        response = self.client.get(reverse("order-success", args=[order.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["order"], order)

    def test_order_success_rejects_other_users_order(self):
        owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass"
        )
        other = User.objects.create_user(
            username="other", email="other@example.com", password="pass"
        )
        order = Order.objects.create(
            user=owner,
            first_name="Order",
            last_name="Owner",
            email="owner@example.com",
            phone="+380501112233",
            address="Main Street 1",
            city="Kyiv",
            postal_code="01001",
            total_price=Decimal("12.00"),
        )
        self.client.force_login(other)

        response = self.client.get(reverse("order-success", args=[order.pk]))

        self.assertEqual(response.status_code, 404)

    def test_order_success_allows_recent_guest_order_from_session(self):
        product = create_product()
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "1"})
        token = self.get_checkout_token()

        checkout_response = self.client.post(reverse("checkout"), checkout_payload(token))
        order = Order.objects.get()
        self.assertRedirects(checkout_response, reverse("order-success", args=[order.pk]))

        response = self.client.get(reverse("order-success", args=[order.pk]))

        self.assertEqual(response.status_code, 200)
