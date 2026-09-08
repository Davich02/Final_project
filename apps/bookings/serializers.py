from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'listing', 'tenant', 'date_start', 'date_end', 'created_at', 'updated_at']
        read_only_fields = ['tenant', 'status']