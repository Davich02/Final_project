from rest_framework import serializers
from .models import Booking
from apps.core.models import BookingStatus
from django.db import transaction

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'tenant', 'date_start', 'date_end', 'created_at', 'updated_at','status']
        read_only_fields = ['tenant', 'status']

    def validate(self, attrs):
        listing = attrs.get('listing')
        date_start = attrs.get('date_start')
        date_end = attrs.get('date_end')

        if date_start and date_end and date_end <= date_start:
            raise serializers.ValidationError({'date_end': 'Дата выезда должна быть позже даты заезда.'})

        # Блокируем строки объявления на время проверки + создания
        with transaction.atomic():
            # select_for_update блокирует запись listing до конца транзакции
            listing = listing.__class__.objects.select_for_update().get(pk=listing.pk)

            doubling = Booking.objects.filter(
                listing=listing,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                date_start__lt=date_end,
                date_end__gt=date_start,
            ).exists()

            if doubling:
                raise serializers.ValidationError('Это жильё уже забронировано на выбранные даты.')

        return attrs