from django.db import models


class AuditCycle(models.Model):
    """
    A physical-verification cycle for a department over a date range
    ("Q3 audit — Engineering dept — 1–15 Jul"). Closing the cycle locks
    it and finalizes the discrepancy report.
    """

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    name = models.CharField(max_length=150)
    department = models.ForeignKey(
        'organization.Department', on_delete=models.SET_NULL, null=True, related_name='audit_cycles',
    )
    auditors = models.ManyToManyField('accounts.User', related_name='audits_conducted', blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AuditItem(models.Model):
    """One row of the audit table: an asset expected at a location, and its verification result."""

    class Verification(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        MISSING = 'missing', 'Missing'
        DAMAGED = 'damaged', 'Damaged'

    cycle = models.ForeignKey(AuditCycle, on_delete=models.CASCADE, related_name='items')
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='audit_items')
    expected_location = models.CharField(max_length=150, blank=True)
    verification = models.CharField(max_length=10, choices=Verification.choices, default=Verification.PENDING)
    notes = models.TextField(blank=True)
    verified_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['asset__tag']
        unique_together = ['cycle', 'asset']

    @property
    def is_discrepancy(self):
        return self.verification in (self.Verification.MISSING, self.Verification.DAMAGED)

    def __str__(self):
        return f"{self.cycle} — {self.asset.tag} — {self.verification}"
