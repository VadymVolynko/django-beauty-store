from modeltranslation.translator import TranslationOptions, register

from catalog.models import Brand, Product


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("description",)
