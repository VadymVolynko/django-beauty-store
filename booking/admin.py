from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from booking.models import Appointment, Service, Specialist, SpecialistPhoto


@admin.register(Service)
class ServiceAdmin(TranslationAdmin):
    list_display = ("name", "price", "duration")
    search_fields = ("name",)


class SpecialistPhotoInline(admin.TabularInline):
    model = SpecialistPhoto
    extra = 1


@admin.register(Specialist)
class SpecialistAdmin(TranslationAdmin):
    list_display = ("name", "experience")
    search_fields = ("name",)
    filter_horizontal = ("services",)
    inlines = [SpecialistPhotoInline]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("user", "specialist", "service", "date", "time", "status", "created_at")
    list_filter = ("status", "specialist", "date")
    search_fields = ("user__username", "specialist__name")
    list_editable = ("status",)
    date_hierarchy = "date"
