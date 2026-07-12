from django.contrib import admin

from .models import AllocationHistory, Asset, AssetUsageEvent


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['tag', 'name', 'category', 'status', 'department', 'current_holder', 'location']
    list_filter = ['status', 'category', 'department']
    search_fields = ['tag', 'name', 'qr_code']
    readonly_fields = ['tag', 'qr_code']


@admin.register(AllocationHistory)
class AllocationHistoryAdmin(admin.ModelAdmin):
    list_display = ['asset', 'employee', 'department', 'action', 'occurred_at']
    list_filter = ['action']
    readonly_fields = ['occurred_at']


@admin.register(AssetUsageEvent)
class AssetUsageEventAdmin(admin.ModelAdmin):
    list_display = ['asset', 'source', 'occurred_at']
    list_filter = ['source']
