from django.contrib import admin

from .models import TransferRequest


@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ['asset', 'from_employee', 'to_employee', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['asset__tag', 'asset__name']
    readonly_fields = ['created_at', 'resolved_at']
