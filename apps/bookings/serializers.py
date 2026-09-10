from rest_framework import serializers
from .models import Booking
from apps.core.models import BookingStatus

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'tenant', 'date_start', 'date_end', 'created_at', 'updated_at','status']
        read_only_fields = ['tenant', 'status']

    def validate(self, attrs):
        listing = attrs.get('listing')
        date_start = attrs.get('date_start')
        date_end = attrs.get('date_end')

        overlapping = Booking.objects.filter(
            listing=listing,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            date_start__lt=date_end,
            date_end__gt=date_start,
        ).exists()

        if overlapping:
            raise serializers.ValidationError('Это жильё уже забронировано на выбранные даты.')

        return attrs

