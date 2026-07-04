from django.contrib.auth.backends import ModelBackend

from accounts.models import User


class EmailBackend(ModelBackend):
    """Authenticate using email instead of username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
