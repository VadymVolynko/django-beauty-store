from django.contrib import admin

from booking.models import Appointment, Service, Specialist


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration")
    search_fields = ("name",)


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ("name", "experience")
    search_fields = ("name",)
    filter_horizontal = ("services",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("user", "specialist", "service", "date", "time", "status", "created_at")
    list_filter = ("status", "specialist", "date")
    search_fields = ("user__username", "specialist__name")
    list_editable = ("status",)
    date_hierarchy = "date"
