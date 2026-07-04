from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from booking.models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["specialist", "service", "date", "time", "comment"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "comment": forms.Textarea(
                attrs={"rows": 3, "placeholder": _("Any additional notes...")}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_date(self):
        appointment_date = self.cleaned_data["date"]
        if appointment_date < timezone.localdate():
            raise forms.ValidationError(_("Choose today or a future date."))
        return appointment_date

    def clean(self):
        cleaned = super().clean()
        specialist = cleaned.get("specialist")
        service = cleaned.get("service")
        date = cleaned.get("date")
        time = cleaned.get("time")

        if specialist and service and not specialist.services.filter(pk=service.pk).exists():
            self.add_error("service", _("This specialist does not offer the selected service."))

        if specialist and date and time:
            conflicting_appointments = Appointment.objects.filter(
                specialist=specialist,
                date=date,
                time=time,
                status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
            )
            if self.instance.pk:
                conflicting_appointments = conflicting_appointments.exclude(pk=self.instance.pk)
            if conflicting_appointments.exists():
                self.add_error("time", _("This specialist is already booked for that time."))

        return cleaned
