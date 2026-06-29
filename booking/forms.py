from django import forms

from booking.models import Appointment, Specialist, Service


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["specialist", "service", "date", "time", "comment"]
        widgets = {
            "date":    forms.DateInput(attrs={"type": "date"}),
            "time":    forms.TimeInput(attrs={"type": "time"}),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Any additional notes…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
