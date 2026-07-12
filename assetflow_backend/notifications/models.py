from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Notification(models.Model):
    """
    One row of the Notifications / Activity Log screen. `related_object`
    is a generic FK so any app (transfers, bookings, maintenance, audits)
    can attach a notification without notifications needing to import them.
    """

    class Category(models.TextChoices):
        ALERT = 'alert', 'Alert'
        APPROVAL = 'approval', 'Approval'
        BOOKING = 'booking', 'Booking'
        GENERAL = 'general', 'General'

    recipient = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='notifications',
    )
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient}: {self.message}"
