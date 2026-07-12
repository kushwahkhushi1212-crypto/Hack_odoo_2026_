import uuid
from django.db import models


class Asset(models.Model):
    """
    A single trackable asset — the row shown in the Asset Directory table
    (tag, name, category, status, location).
    """

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        ALLOCATED = 'allocated', 'Allocated'
        MAINTENANCE = 'maintenance', 'Under Maintenance'
        RETIRED = 'retired', 'Retired'

    tag = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        'organization.Category', on_delete=models.PROTECT, related_name='assets',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assets',
    )
    current_holder = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='held_assets',
    )
    location = models.CharField(max_length=150, blank=True)
    qr_code = models.CharField(max_length=64, unique=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    service_due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.tag:
            last = Asset.objects.order_by('id').last()
            next_id = (last.id + 1) if last else 1
            self.tag = f"AF-{next_id:04d}"
        if not self.qr_code:
            self.qr_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tag} · {self.name}"

    @property
    def is_idle(self):
        """True if the asset has had no activity (booking/use) in 30+ days."""
        from django.utils import timezone
        last_use = self.usage_events.order_by('-occurred_at').first()
        if not last_use:
            return (timezone.now() - self.created_at).days > 30
        return (timezone.now() - last_use.occurred_at).days > 30


class AllocationHistory(models.Model):
    """
    Immutable log entry every time an asset is allocated to / returned from
    an employee — the "Allocation history" panel on the Transfer screen.
    """

    class Action(models.TextChoices):
        ALLOCATED = 'allocated', 'Allocated'
        RETURNED = 'returned', 'Returned'
        TRANSFERRED = 'transferred', 'Transferred'

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='history')
    employee = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='+')
    department = models.ForeignKey('organization.Department', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    condition = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at']
        verbose_name_plural = 'Allocation history'

    def __str__(self):
        return f"{self.asset.tag} — {self.action} — {self.occurred_at:%Y-%m-%d}"


class AssetUsageEvent(models.Model):
    """
    Generic "this asset was used" ping, written by bookings/transfers/
    maintenance-resolution so Reports can compute most-used / idle assets
    without each app needing to know about the others' models.
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='usage_events')
    source = models.CharField(max_length=30)  # 'booking', 'transfer', 'maintenance'
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at']
