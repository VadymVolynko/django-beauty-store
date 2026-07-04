from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from cart.cart import CART_SESSION_KEY
from catalog.models import Brand, Category, Product


def create_product():
    category = Category.objects.create(name="Masks", slug="masks")
    brand = Brand.objects.create(name="Calm Skin", slug="calm-skin")
    return Product.objects.create(
        category=category,
        brand=brand,
        name="Clarifying Mask",
        slug="clarifying-mask",
        description="A calming mask.",
        price="15.50",
        stock=8,
        is_available=True,
    )


class CartViewTests(TestCase):
    def test_add_update_and_remove_product_in_session_cart(self):
        product = create_product()

        add_response = self.client.post(
            reverse("cart-add", args=[product.id]), {"quantity": "2"}
        )
        self.assertRedirects(add_response, reverse("cart"))
        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(product.id)]["quantity"], 2
        )

        update_response = self.client.post(
            reverse("cart-update", args=[product.id]), {"quantity": "4"}
        )
        self.assertRedirects(update_response, reverse("cart"))
        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(product.id)]["quantity"], 4
        )

        remove_response = self.client.post(reverse("cart-remove", args=[product.id]))
        self.assertRedirects(remove_response, reverse("cart"))
        self.assertNotIn(str(product.id), self.client.session[CART_SESSION_KEY])

    def test_update_to_zero_removes_product(self):
        product = create_product()
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "1"})

        self.client.post(reverse("cart-update", args=[product.id]), {"quantity": "0"})

        self.assertNotIn(str(product.id), self.client.session[CART_SESSION_KEY])

    def test_adding_same_product_twice_accumulates_quantity(self):
        product = create_product()

        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "2"})
        self.client.post(reverse("cart-add", args=[product.id]), {"quantity": "3"})

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(product.id)]["quantity"], 5
        )

    def test_cart_total_price_reflects_all_items(self):
        product_a = create_product()
        product_b = Product.objects.create(
            category=product_a.category,
            brand=product_a.brand,
            name="Second Item",
            slug="second-item",
            description="Another product.",
            price="10.00",
            stock=5,
            is_available=True,
        )

        self.client.post(reverse("cart-add", args=[product_a.id]), {"quantity": "2"})
        self.client.post(reverse("cart-add", args=[product_b.id]), {"quantity": "1"})

        response = self.client.get(reverse("cart"))

        self.assertEqual(response.context["cart"].total_price, Decimal("41.00"))

    def test_removing_product_not_in_cart_is_a_no_op(self):
        product = create_product()

        response = self.client.post(reverse("cart-remove", args=[product.id]))

        self.assertRedirects(response, reverse("cart"))
        self.assertNotIn(str(product.id), self.client.session.get(CART_SESSION_KEY, {}))

    def test_adding_nonexistent_product_returns_404(self):
        response = self.client.post(reverse("cart-add", args=[999999]), {"quantity": "1"})

        self.assertEqual(response.status_code, 404)

    def test_empty_cart_has_zero_total_and_length(self):
        response = self.client.get(reverse("cart"))

        self.assertEqual(response.context["cart"].total_price, Decimal("0"))
        self.assertEqual(len(response.context["cart"]), 0)

# Create your tests here.
