from django.core.exceptions import ValidationError
from django.db import models


class TransferRequest(models.Model):
    """
    "An asset already allocated cannot be re-assigned directly — submit a
    transfer request instead." Covers both first-time allocation (from
    unallocated) and employee-to-employee transfer.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='transfer_requests')
    from_employee = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_from',
    )
    to_employee = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='transfers_to',
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='transfer_requests_made',
    )
    resolved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_requests_resolved',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.from_employee_id and self.from_employee_id == self.to_employee_id:
            raise ValidationError('Cannot transfer an asset to its current holder.')

    def __str__(self):
        return f"{self.asset.tag} → {self.to_employee} ({self.status})"
