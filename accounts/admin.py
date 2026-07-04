from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import EmailVerificationToken, User


@admin.register(User)
class BeautyStoreUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Contact", {"fields": ("phone_number",)}),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
