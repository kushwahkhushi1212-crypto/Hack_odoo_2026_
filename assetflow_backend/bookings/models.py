from django.db import models


class BookableResource(models.Model):
    """
    A resource that can be reserved in time slots — a meeting room, a
    shared vehicle, etc. Optionally tied to a physical Asset record.
    """
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    asset = models.OneToOneField(
        'assets.Asset', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookable_resource',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Booking(models.Model):
    """
    A reservation of a BookableResource for a time window. Overlapping
    CONFIRMED bookings on the same resource are rejected outright (the
    calendar screen never shows a double-booked slot); a second request
    for an already-held slot is stored as CONFLICT for manual resolution,
    matching the dashed "conflict" slot shown in the UI.
    """

    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        CONFLICT = 'conflict', 'Conflict — needs manual resolution'
        CANCELLED = 'cancelled', 'Cancelled'

    resource = models.ForeignKey(BookableResource, on_delete=models.CASCADE, related_name='bookings')
    booked_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def overlaps(self, other_start, other_end):
        return self.start_time < other_end and other_start < self.end_time

    def __str__(self):
        return f"{self.resource} — {self.start_time:%Y-%m-%d %H:%M} ({self.status})"
