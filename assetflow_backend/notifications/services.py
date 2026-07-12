"""
Small helper other apps call to raise a notification without importing
DRF views or worrying about generic-FK plumbing directly.
"""
from django.contrib.contenttypes.models import ContentType

from .models import Notification


def notify(recipients, category, message, related_object=None):
    """
    Create one Notification per recipient.

    recipients: iterable of User instances (falsy/None entries are skipped)
    category: one of Notification.Category values
    message: short display string, e.g. "Transfer approved — AF-0033 ..."
    related_object: optional model instance the notification points to
    """
    content_type = ContentType.objects.get_for_model(related_object) if related_object else None
    object_id = related_object.pk if related_object else None

    created = []
    for user in recipients or []:
        if not user:
            continue
        created.append(Notification(
            recipient=user, category=category, message=message,
            content_type=content_type, object_id=object_id,
        ))
    return Notification.objects.bulk_create(created)
