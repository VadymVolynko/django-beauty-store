from django import forms
from django.utils.translation import gettext_lazy as _

from reviews.models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} ★") for i in range(1, 6)],
                attrs={"class": "form-control-custom"},
            ),
            "text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control-custom",
                    "placeholder": _("Share your experience..."),
                }
            ),
        }
