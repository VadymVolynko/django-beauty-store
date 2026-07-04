from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from catalog.models import Brand, Category, Product
from reviews.models import Review

OWNER_SESSION_KEY = "owner_access"


def make_owner_session(client):
    session = client.session
    session[OWNER_SESSION_KEY] = True
    session.save()


def create_product(**overrides):
    category = Category.objects.create(name="Serums", slug="serums")
    brand = Brand.objects.create(name="Glow Lab", slug="glow-lab")
    defaults = {
        "category": category,
        "brand": brand,
        "name": "Retinol Serum",
        "slug": "retinol-serum",
        "description": "A gentle nightly serum.",
        "price": "29.90",
        "stock": 10,
        "is_available": True,
        "is_featured": True,
    }
    defaults.update(overrides)
    return Product.objects.create(**defaults)


class CatalogViewTests(TestCase):
    def test_home_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("home"))

        self.assertRedirects(response, reverse("login"))

    def test_home_is_available_for_authenticated_user(self):
        user = User.objects.create_user(
            username="customer", email="customer@example.com", password="pass"
        )
        product = create_product()
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(product, response.context["products"])

    def test_product_review_is_created_once_per_user(self):
        user = User.objects.create_user(
            username="reviewer", email="reviewer@example.com", password="pass"
        )
        product = create_product()
        self.client.force_login(user)

        response = self.client.post(
            reverse("product", args=[product.slug]),
            {"rating": 5, "text": "Excellent texture."},
        )

        self.assertRedirects(response, reverse("product", args=[product.slug]))
        review = Review.objects.get(product=product, user=user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "Excellent texture.")

    def test_product_detail_page_returns_200_with_expected_context(self):
        product = create_product()

        response = self.client.get(reverse("product", args=[product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"], product)
        self.assertIn("reviews", response.context)

    def test_brand_list_view_returns_all_brands(self):
        create_product()
        Brand.objects.create(name="Second Brand", slug="second-brand")

        response = self.client.get(reverse("catalog"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["brands"]), 2)

    def test_brand_products_view_filters_by_category_and_search(self):
        product = create_product()
        other_category = Category.objects.create(name="Cleansers", slug="cleansers")
        Product.objects.create(
            category=other_category,
            brand=product.brand,
            name="Foam Wash",
            slug="foam-wash",
            description="A gentle foam cleanser.",
            price="12.00",
            stock=5,
            is_available=True,
        )

        response = self.client.get(
            reverse("catalog-brand", args=[product.brand.slug]),
            {"category": product.category.slug},
        )
        self.assertEqual(list(response.context["products"]), [product])

        response = self.client.get(
            reverse("catalog-brand", args=[product.brand.slug]), {"q": "Retinol"}
        )
        self.assertEqual(list(response.context["products"]), [product])

        response = self.client.get(
            reverse("catalog-brand", args=[product.brand.slug]), {"q": "Nonexistent"}
        )
        self.assertEqual(list(response.context["products"]), [])


class OwnerProductManagementAccessTests(TestCase):
    def test_product_manage_list_redirects_without_owner_session(self):
        response = self.client.get(reverse("owner-products"))

        self.assertRedirects(response, reverse("login"))

    def test_product_manage_list_accessible_with_owner_session(self):
        create_product()
        make_owner_session(self.client)

        response = self.client.get(reverse("owner-products"))

        self.assertEqual(response.status_code, 200)

    def test_product_create_requires_owner_session(self):
        category = Category.objects.create(name="Oils", slug="oils")
        brand = Brand.objects.create(name="Oil Co", slug="oil-co")

        response = self.client.post(
            reverse("owner-product-add"),
            {
                "category": category.id,
                "brand": brand.id,
                "name": "Face Oil",
                "slug": "face-oil",
                "description": "Nourishing oil.",
                "price": "20.00",
                "stock": "5",
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertFalse(Product.objects.filter(slug="face-oil").exists())

    def test_owner_can_create_edit_and_delete_product(self):
        category = Category.objects.create(name="Oils", slug="oils")
        brand = Brand.objects.create(name="Oil Co", slug="oil-co")
        make_owner_session(self.client)

        create_response = self.client.post(
            reverse("owner-product-add"),
            {
                "category": category.id,
                "brand": brand.id,
                "name": "Face Oil",
                "slug": "face-oil",
                "description": "Nourishing oil.",
                "price": "20.00",
                "stock": "5",
            },
        )
        self.assertRedirects(create_response, reverse("owner-products"))
        product = Product.objects.get(slug="face-oil")

        edit_response = self.client.post(
            reverse("owner-product-edit", args=[product.slug]),
            {
                "category": category.id,
                "brand": brand.id,
                "name": "Face Oil Deluxe",
                "slug": "face-oil",
                "description": "Nourishing oil.",
                "price": "25.00",
                "stock": "5",
            },
        )
        self.assertRedirects(edit_response, reverse("owner-products"))
        product.refresh_from_db()
        self.assertEqual(product.name, "Face Oil Deluxe")

        delete_response = self.client.post(reverse("owner-product-delete", args=[product.slug]))
        self.assertRedirects(delete_response, reverse("owner-products"))
        self.assertFalse(Product.objects.filter(slug="face-oil").exists())

# Create your tests here.
