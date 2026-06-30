from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label="First name",
        widget=forms.TextInput(),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label="Last name",
        widget=forms.TextInput(),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", "Passwords do not match.")
            else:
                try:
                    validate_password(p1)
                except forms.ValidationError as e:
                    self.add_error("password1", e)
        return cleaned
