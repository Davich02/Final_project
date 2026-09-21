from rest_framework import serializers
from django.utils import timezone
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'tenant', 'date_start', 'date_end', 'created_at', 'updated_at','status']
        read_only_fields = ['tenant', 'status']

    def validate(self, attrs):
        # здесь только проверки, которым не нужна блокировка БД;
        # пересечение дат проверяется во view внутри транзакции
        listing = attrs.get('listing')
        date_start = attrs.get('date_start')
        date_end = attrs.get('date_end')
        user = self.context['request'].user

        if date_end <= date_start:
            raise serializers.ValidationError({'date_end': 'Дата выезда должна быть позже даты заезда.'})

        if date_start < timezone.now().date():
            raise serializers.ValidationError({'date_start': 'Нельзя забронировать даты в прошлом.'})

        if not listing.is_active:
            raise serializers.ValidationError({'listing': 'Это объявление сейчас неактивно.'})

        if listing.owner == user:
            raise serializers.ValidationError({'listing': 'Нельзя забронировать своё же объявление.'})

        return attrs
