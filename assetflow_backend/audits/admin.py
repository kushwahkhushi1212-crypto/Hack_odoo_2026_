from django.contrib import admin

from .models import AuditCycle, AuditItem


class AuditItemInline(admin.TabularInline):
    model = AuditItem
    extra = 0


@admin.register(AuditCycle)
class AuditCycleAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'department']
    filter_horizontal = ['auditors']
    inlines = [AuditItemInline]


@admin.register(AuditItem)
class AuditItemAdmin(admin.ModelAdmin):
    list_display = ['cycle', 'asset', 'expected_location', 'verification']
    list_filter = ['verification']
