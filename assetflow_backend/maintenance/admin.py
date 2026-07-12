from django.contrib import admin

from .models import MaintenanceStatusLog, MaintenanceTicket


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ['asset', 'issue', 'status', 'priority', 'technician', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['asset__tag', 'issue']


@admin.register(MaintenanceStatusLog)
class MaintenanceStatusLogAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'from_status', 'to_status', 'changed_by', 'changed_at']
