from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from catalog.models import Brand, Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(TranslationAdmin):
    list_display = ("name", "slug", "image")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = (
        "name",
        "category",
        "brand",
        "price",
        "stock",
        "is_available",
        "is_featured",
    )

    list_filter = (
        "category",
        "brand",
        "is_available",
        "is_featured",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

