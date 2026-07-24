"""
Management command: python manage.py create_test_user
Creates (or resets) a single active, pre-verified account so reviewers
without email access can log in and browse the storefront.
"""
from django.core.management.base import BaseCommand

from accounts.models import User

TEST_USERNAME = "user"
TEST_EMAIL = "user@example.com"
TEST_PASSWORD = "user12345"


class Command(BaseCommand):
    help = "Create (or reset) the standard test user account"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username=TEST_USERNAME,
            defaults={"email": TEST_EMAIL, "is_active": True},
        )
        user.email = TEST_EMAIL
        user.is_active = True
        user.set_password(TEST_PASSWORD)
        user.save()

        action = "Created" if created else "Reset"
        self.stdout.write(self.style.SUCCESS(
            f"{action} test user: {TEST_USERNAME} / {TEST_PASSWORD}"
        ))
