import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model = the "employee profile" described on the AssetFlow
    login screen: signing up creates a profile, admin access is granted
    afterwards by the organization (see role field + is_org_admin()).
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Department Manager'
        EMPLOYEE = 'employee', 'Employee'

    employee_id = models.CharField(
        max_length=20, unique=True, editable=False, blank=True
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.ForeignKey(
        'organization.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
    )
    designation = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active_employee = models.BooleanField(default=True)
    date_joined_org = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"EMP-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_org_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def initials(self):
        name = self.get_full_name() or self.username
        parts = name.split()
        return ''.join(p[0].upper() for p in parts[:2]) if parts else '??'
