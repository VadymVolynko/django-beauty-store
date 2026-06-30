from django.urls import path

from accounts.views import login_view, logout_view, profile_view, register_view, verify_email_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("verify/<uuid:token>/", verify_email_view, name="verify-email"),
]
