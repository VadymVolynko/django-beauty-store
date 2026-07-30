"""
Management command: python manage.py create_admin_user
Creates (or resets) a Django admin (superuser) account from the
ADMIN_EMAIL / ADMIN_PASSWORD environment variables, so the real
credentials never appear in source control. No-op if either is unset.
"""
from decouple import config
from django.core.management.base import BaseCommand

from accounts.models import User

ADMIN_EMAIL = config("ADMIN_EMAIL", default="")
ADMIN_PASSWORD = config("ADMIN_PASSWORD", default="")


class Command(BaseCommand):
    help = "Create (or reset) the Django admin superuser from ADMIN_EMAIL/ADMIN_PASSWORD"

    def handle(self, *args, **options):
        if not ADMIN_EMAIL or not ADMIN_PASSWORD:
            self.stdout.write("ADMIN_EMAIL/ADMIN_PASSWORD not set, skipping admin user setup")
            return

        user, created = User.objects.get_or_create(
            username=ADMIN_EMAIL,
            defaults={"email": ADMIN_EMAIL},
        )
        user.email = ADMIN_EMAIL
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(ADMIN_PASSWORD)
        user.save()

        action = "Created" if created else "Reset"
        self.stdout.write(self.style.SUCCESS(f"{action} admin user: {ADMIN_EMAIL}"))
