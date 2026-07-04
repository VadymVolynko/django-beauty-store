from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from catalog.models import Product
from catalog.tests import create_product
from reviews.forms import ReviewForm
from reviews.models import Review


def create_review(**overrides):
    product = overrides.pop("product", None) or create_product()
    user = overrides.pop("user", None)
    if user is None:
        user = User.objects.create_user(
            username="default-reviewer", email="default-reviewer@example.com", password="pass"
        )
    defaults = {"product": product, "user": user, "rating": 4, "text": "Nice product."}
    defaults.update(overrides)
    return Review.objects.create(**defaults)


class ReviewModelTests(TestCase):
    def test_str_includes_user_product_and_rating(self):
        review = create_review(rating=5)

        self.assertIn(review.user.username, str(review))
        self.assertIn(review.product.name, str(review))
        self.assertIn("5", str(review))

    def test_rating_below_minimum_fails_validation(self):
        product = create_product()
        user = User.objects.create_user(username="u1", email="u1@example.com", password="pass")
        review = Review(product=product, user=user, rating=0, text="Too low")

        with self.assertRaises(Exception):
            review.full_clean()

    def test_rating_above_maximum_fails_validation(self):
        product = create_product()
        user = User.objects.create_user(username="u2", email="u2@example.com", password="pass")
        review = Review(product=product, user=user, rating=6, text="Too high")

        with self.assertRaises(Exception):
            review.full_clean()

    def test_same_user_cannot_review_same_product_twice(self):
        product = create_product()
        user = User.objects.create_user(username="u3", email="u3@example.com", password="pass")
        create_review(product=product, user=user)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_review(product=product, user=user)

    def test_same_user_can_review_different_products(self):
        user = User.objects.create_user(username="u4", email="u4@example.com", password="pass")
        product_a = create_product(slug="product-a")
        product_b = Product.objects.create(
            category=product_a.category,
            brand=product_a.brand,
            name="Second Product",
            slug="product-b",
            description="Another product.",
            price="19.90",
            stock=5,
            is_available=True,
        )

        create_review(product=product_a, user=user)
        create_review(product=product_b, user=user)

        self.assertEqual(Review.objects.filter(user=user).count(), 2)


class ReviewFormTests(TestCase):
    def test_valid_data_is_accepted(self):
        form = ReviewForm(data={"rating": 5, "text": "Great!"})

        self.assertTrue(form.is_valid())

    def test_rating_outside_choices_is_rejected(self):
        form = ReviewForm(data={"rating": 6, "text": "Too high"})

        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_missing_text_is_rejected(self):
        form = ReviewForm(data={"rating": 3, "text": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("text", form.errors)


class ReviewSubmissionViewTests(TestCase):
    def test_anonymous_user_cannot_submit_review(self):
        product = create_product()

        response = self.client.post(
            reverse("product", args=[product.slug]),
            {"rating": 5, "text": "Should not be saved"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.filter(product=product).count(), 0)

    def test_authenticated_user_without_review_sees_form(self):
        user = User.objects.create_user(username="viewer", email="viewer@example.com", password="pass")
        product = create_product()
        self.client.force_login(user)

        response = self.client.get(reverse("product", args=[product.slug]))

        self.assertIsNotNone(response.context["review_form"])
        self.assertIsNone(response.context["user_review"])

    def test_user_with_existing_review_does_not_see_form_again(self):
        user = User.objects.create_user(username="repeat", email="repeat@example.com", password="pass")
        product = create_product()
        create_review(product=product, user=user)
        self.client.force_login(user)

        response = self.client.get(reverse("product", args=[product.slug]))

        self.assertIsNone(response.context["review_form"])
        self.assertIsNotNone(response.context["user_review"])

    def test_posted_review_appears_in_product_reviews(self):
        user = User.objects.create_user(username="poster", email="poster@example.com", password="pass")
        product = create_product()
        self.client.force_login(user)

        self.client.post(
            reverse("product", args=[product.slug]),
            {"rating": 4, "text": "Solid pick."},
        )

        response = self.client.get(reverse("product", args=[product.slug]))
        self.assertIn(product.reviews.get(user=user), response.context["reviews"])
