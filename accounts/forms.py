from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label=_("First name"),
        widget=forms.TextInput(),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label=_("Last name"),
        widget=forms.TextInput(),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(),
    )
    phone_number = forms.CharField(
        max_length=30,
        required=False,
        label=_("Phone number"),
        widget=forms.TextInput(),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("An account with this email already exists."))
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", _("Passwords do not match."))
            else:
                try:
                    validate_password(p1)
                except forms.ValidationError as e:
                    self.add_error("password1", e)
        return cleaned
