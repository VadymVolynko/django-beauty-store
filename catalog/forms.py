from django import forms
from django.utils.translation import gettext_lazy as _

from catalog.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "name",
            "slug",
            "description",
            "price",
            "image",
            "stock",
            "is_available",
            "is_featured",
        ]
        labels = {
            "category": _("Category"),
            "brand": _("Brand"),
            "name": _("Name"),
            "slug": _("Slug"),
            "description": _("Description"),
            "price": _("Price"),
            "image": _("Image"),
            "stock": _("Stock"),
            "is_available": _("Available"),
            "is_featured": _("Featured"),
        }
        widgets = {
            "category": forms.Select(attrs={"class": "form-control-custom"}),
            "brand": forms.Select(attrs={"class": "form-control-custom"}),
            "name": forms.TextInput(attrs={"class": "form-control-custom"}),
            "slug": forms.TextInput(attrs={"class": "form-control-custom"}),
            "description": forms.Textarea(attrs={"class": "form-control-custom", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "form-control-custom"}),
            "stock": forms.NumberInput(attrs={"class": "form-control-custom"}),
        }
