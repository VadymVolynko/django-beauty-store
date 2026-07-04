from datetime import datetime, timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from booking.models import Appointment, Service, Specialist


def create_booking_data():
    service = Service.objects.create(
        name="Skin Consultation",
        description="Personal skin routine consultation.",
        price="40.00",
        duration=60,
    )
    specialist = Specialist.objects.create(
        name="Olena Smith",
        bio="Certified cosmetologist.",
        experience=6,
    )
    specialist.services.add(service)
    return service, specialist


def appointment_date(days=30):
    return timezone.localdate() + timedelta(days=days)


def appointment_payload(service, specialist, *, days=30, appointment_time="14:30"):
    return {
        "service": service.id,
        "specialist": specialist.id,
        "date": appointment_date(days).isoformat(),
        "time": appointment_time,
        "comment": "Sensitive skin.",
    }


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class BookingViewTests(TestCase):
    def test_authenticated_user_can_create_appointment(self):
        user = User.objects.create_user(
            username="client", email="client@example.com", password="pass"
        )
        service, specialist = create_booking_data()
        self.client.force_login(user)

        response = self.client.post(
            reverse("appointment-create"),
            appointment_payload(service, specialist),
        )

        self.assertRedirects(response, reverse("appointment-list"))
        appointment = Appointment.objects.get()
        self.assertEqual(appointment.user, user)
        self.assertEqual(appointment.service, service)
        self.assertEqual(appointment.specialist, specialist)
        self.assertEqual(appointment.date, appointment_date())
        self.assertEqual(appointment.time, datetime.strptime("14:30", "%H:%M").time())

    def test_appointment_list_only_shows_current_users_appointments(self):
        service, specialist = create_booking_data()
        current_user = User.objects.create_user(
            username="current", email="current@example.com", password="pass"
        )
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="pass"
        )
        own_appointment = Appointment.objects.create(
            user=current_user,
            service=service,
            specialist=specialist,
            date=appointment_date(),
            time="14:30",
        )
        Appointment.objects.create(
            user=other_user,
            service=service,
            specialist=specialist,
            date=appointment_date(31),
            time="15:30",
        )
        self.client.force_login(current_user)

        response = self.client.get(reverse("appointment-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["appointments"]), [own_appointment])

    def test_cannot_book_past_date(self):
        user = User.objects.create_user(
            username="client", email="client@example.com", password="pass"
        )
        service, specialist = create_booking_data()
        self.client.force_login(user)

        response = self.client.post(
            reverse("appointment-create"),
            appointment_payload(service, specialist, days=-1),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(Appointment.objects.count(), 0)

    def test_cannot_double_book_specialist_slot(self):
        first_user = User.objects.create_user(
            username="first", email="first@example.com", password="pass"
        )
        second_user = User.objects.create_user(
            username="second", email="second@example.com", password="pass"
        )
        service, specialist = create_booking_data()
        Appointment.objects.create(
            user=first_user,
            service=service,
            specialist=specialist,
            date=appointment_date(),
            time="14:30",
        )
        self.client.force_login(second_user)

        response = self.client.post(
            reverse("appointment-create"),
            appointment_payload(service, specialist),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(Appointment.objects.count(), 1)

    def test_cancelled_appointment_does_not_block_slot(self):
        first_user = User.objects.create_user(
            username="first", email="first@example.com", password="pass"
        )
        second_user = User.objects.create_user(
            username="second", email="second@example.com", password="pass"
        )
        service, specialist = create_booking_data()
        Appointment.objects.create(
            user=first_user,
            service=service,
            specialist=specialist,
            date=appointment_date(),
            time="14:30",
            status=Appointment.Status.CANCELLED,
        )
        self.client.force_login(second_user)

        response = self.client.post(
            reverse("appointment-create"),
            appointment_payload(service, specialist),
        )

        self.assertRedirects(response, reverse("appointment-list"))
        self.assertEqual(Appointment.objects.count(), 2)

    def test_specialist_must_offer_selected_service(self):
        user = User.objects.create_user(
            username="client", email="client@example.com", password="pass"
        )
        offered_service, specialist = create_booking_data()
        other_service = Service.objects.create(
            name="Peeling",
            description="Gentle chemical peel.",
            price="55.00",
            duration=45,
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("appointment-create"),
            appointment_payload(other_service, specialist),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(Appointment.objects.count(), 0)
        self.assertTrue(specialist.services.filter(pk=offered_service.pk).exists())
