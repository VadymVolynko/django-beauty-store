from django.urls import path

from booking.views import (
    AppointmentCreateView,
    AppointmentDeleteView,
    AppointmentListView,
    AppointmentUpdateView,
    ServiceListView,
    SpecialistListView,
)

urlpatterns = [
    path("services/",                          ServiceListView.as_view(),      name="service-list"),
    path("specialists/",                       SpecialistListView.as_view(),   name="specialist-list"),
    path("appointments/",                      AppointmentListView.as_view(),  name="appointment-list"),
    path("appointments/book/",                 AppointmentCreateView.as_view(), name="appointment-create"),
    path("appointments/<int:pk>/edit/",        AppointmentUpdateView.as_view(), name="appointment-update"),
    path("appointments/<int:pk>/cancel/",      AppointmentDeleteView.as_view(), name="appointment-delete"),
]
