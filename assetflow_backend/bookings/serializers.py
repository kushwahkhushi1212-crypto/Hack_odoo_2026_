from rest_framework import serializers

from accounts.serializers import EmployeeMiniSerializer
from .models import BookableResource, Booking


class BookableResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookableResource
        fields = ['id', 'name', 'location', 'capacity', 'asset', 'is_active']
        read_only_fields = ['id']


class BookingSerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    booked_by_detail = EmployeeMiniSerializer(source='booked_by', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'resource', 'resource_name', 'booked_by', 'booked_by_detail',
            'start_time', 'end_time', 'purpose', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'booked_by', 'created_at']

    def validate(self, attrs):
        start, end = attrs.get('start_time'), attrs.get('end_time')
        if start and end and start >= end:
            raise serializers.ValidationError('start_time must be before end_time.')
        return attrs
