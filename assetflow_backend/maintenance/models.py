from django.db import models


class MaintenanceTicket(models.Model):
    """
    One card on the Maintenance kanban board. The five statuses are the
    five kanban columns: Pending → Approved → Technician assigned →
    In progress → Resolved. Approving moves the linked asset to
    "Under maintenance"; resolving returns it to "Available".
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        ASSIGNED = 'assigned', 'Technician assigned'
        IN_PROGRESS = 'in_progress', 'In progress'
        RESOLVED = 'resolved', 'Resolved'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='maintenance_tickets')
    reported_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='maintenance_reported',
    )
    technician = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_assigned',
    )
    issue = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.asset.tag} — {self.issue} ({self.status})"


class MaintenanceStatusLog(models.Model):
    """Audit trail of every kanban column move, for the maintenance-frequency report."""
    ticket = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE, related_name='status_log')
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
