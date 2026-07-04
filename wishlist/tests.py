from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from catalog.models import Brand, Category, Product
from wishlist.models import WishlistItem


def create_product():
    category = Category.objects.create(name="Toners", slug="toners")
    brand = Brand.objects.create(name="Fresh Lab", slug="fresh-lab")
    return Product.objects.create(
        category=category,
        brand=brand,
        name="Essential Tonic",
        slug="essential-tonic",
        description="Daily toning care.",
        price="18.00",
        stock=12,
        is_available=True,
    )


class WishlistViewTests(TestCase):
    def test_wishlist_requires_login(self):
        response = self.client.get(reverse("wishlist"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('wishlist')}")

    def test_add_product_to_wishlist_once(self):
        user = User.objects.create_user(
            username="wisher", email="wisher@example.com", password="pass"
        )
        product = create_product()
        self.client.force_login(user)

        self.client.post(reverse("wishlist-add", args=[product.id]))
        self.client.post(reverse("wishlist-add", args=[product.id]))

        self.assertEqual(
            WishlistItem.objects.filter(user=user, product=product).count(),
            1,
        )

    def test_unsafe_next_url_falls_back_to_catalog(self):
        user = User.objects.create_user(
            username="safe", email="safe@example.com", password="pass"
        )
        product = create_product()
        self.client.force_login(user)

        response = self.client.post(
            reverse("wishlist-add", args=[product.id]),
            {"next": "https://evil.example/path"},
        )

        self.assertRedirects(response, reverse("catalog"))

    def test_remove_product_from_wishlist(self):
        user = User.objects.create_user(
            username="remover", email="remover@example.com", password="pass"
        )
        product = create_product()
        WishlistItem.objects.create(user=user, product=product)
        self.client.force_login(user)

        self.client.post(reverse("wishlist-remove", args=[product.id]))

        self.assertEqual(WishlistItem.objects.filter(user=user, product=product).count(), 0)

    def test_wishlist_add_requires_login(self):
        product = create_product()

        response = self.client.post(reverse("wishlist-add", args=[product.id]))

        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('wishlist-add', args=[product.id])}"
        )
        self.assertEqual(WishlistItem.objects.count(), 0)

    def test_wishlist_only_shows_current_users_items(self):
        owner = User.objects.create_user(
            username="owner1", email="owner1@example.com", password="pass"
        )
        other = User.objects.create_user(
            username="other1", email="other1@example.com", password="pass"
        )
        product = create_product()
        WishlistItem.objects.create(user=owner, product=product)
        self.client.force_login(other)

        response = self.client.get(reverse("wishlist"))

        self.assertEqual(len(response.context["page_obj"]), 0)

# Create your tests here.
