from modeltranslation.translator import TranslationOptions, register

from booking.models import Service, Specialist


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Specialist)
class SpecialistTranslationOptions(TranslationOptions):
    fields = ("bio",)
