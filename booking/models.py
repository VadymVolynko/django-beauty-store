from django.contrib.auth.models import User
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Specialist(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField()
    photo = models.ImageField(upload_to="specialists/", blank=True, null=True)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    services = models.ManyToManyField(Service, related_name="specialists")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING   = "pending",   "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name="appointments")
    service    = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="appointments")
    date       = models.DateField()
    time       = models.TimeField()
    status     = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"{self.user.username} — {self.specialist.name} ({self.date})"
