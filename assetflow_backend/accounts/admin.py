from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['employee_id', 'email', 'first_name', 'last_name', 'role',
                     'department', 'is_active_employee', 'is_staff']
    list_filter = ['role', 'department', 'is_active_employee', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'employee_id']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('AssetFlow profile', {
            'fields': ('employee_id', 'role', 'department', 'designation',
                       'phone', 'avatar', 'is_active_employee', 'date_joined_org')
        }),
    )
    readonly_fields = ['employee_id']
