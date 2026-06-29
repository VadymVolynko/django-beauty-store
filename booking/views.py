from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from booking.forms import AppointmentForm
from booking.models import Appointment, Service, Specialist


class ServiceListView(ListView):
    model = Service
    template_name = "booking/service_list.html"
    context_object_name = "services"


class SpecialistListView(ListView):
    model = Specialist
    template_name = "booking/specialist_list.html"
    context_object_name = "specialists"


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "booking/appointment_form.html"
    success_url = reverse_lazy("appointment-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = "booking/appointment_list.html"
    context_object_name = "appointments"

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).select_related(
            "specialist", "service"
        )


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "booking/appointment_form.html"
    success_url = reverse_lazy("appointment-list")

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)


class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = "booking/appointment_confirm_delete.html"
    success_url = reverse_lazy("appointment-list")

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)
