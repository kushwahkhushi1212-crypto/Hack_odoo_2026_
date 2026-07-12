from django.contrib import admin

from .models import BookableResource, Booking


@admin.register(BookableResource)
class BookableResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'capacity', 'is_active']
    list_filter = ['is_active']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['resource', 'booked_by', 'start_time', 'end_time', 'status']
    list_filter = ['status', 'resource']
    readonly_fields = ['created_at']
