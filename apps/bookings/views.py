from rest_framework import viewsets
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from apps.reviews.serializers import ReviewSerializer
from apps.core.models import BookingStatus
from apps.listings.models import Listing
from django.db import transaction
from django.db.models import Q


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    # без put/patch/delete, статус меняем только через actions
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        # для swagger
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        user = self.request.user
        return Booking.objects.filter(Q(tenant=user) | Q(listing__owner=user))

    def perform_create(self, serializer):
        data = serializer.validated_data
        # блокируем объявление, чтобы не было двойной брони при одновременных запросах
        with transaction.atomic():
            listing = Listing.objects.select_for_update().get(pk=data['listing'].pk)

            overlap = Booking.objects.filter(
                listing=listing,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                date_start__lt=data['date_end'],
                date_end__gt=data['date_start'],
            ).exists()
            if overlap:
                raise ValidationError('Это жильё уже забронировано на выбранные даты.')

            # tenant подставляется сервером
            serializer.save(tenant=self.request.user)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        # арендатор отменяет бронь
        booking = self.get_object()

        if booking.tenant != request.user:
            return Response({'detail': 'Это не ваше бронирование.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            return Response({'detail': 'Отменить можно только бронь в статусе pending или confirmed.'},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = BookingStatus.CANCELLED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=['post'], url_path='review')
    def leave_review(self, request, pk=None):
        # валидация отзыва, можно оставить только после окончания брони и только на своё бронирование
        booking = self.get_object()

        if booking.tenant != request.user:
            return Response(
                {'detail': 'Это не ваше бронирование.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if booking.status != BookingStatus.COMPLETED:
            return Response(
                {'detail': 'Отзыв можно оставить только после завершённого проживания.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if hasattr(booking, 'review'):
            return Response(
                {'detail': 'Отзыв уже оставлен.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(booking=booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        # арендодатель подтверждает бронь
        booking = self.get_object()

        if booking.listing.owner != request.user:
            return Response({'detail': 'Вы не владелец этого объявления.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != BookingStatus.PENDING:
            return Response({'detail': 'Подтвердить можно только бронь в статусе pending.'},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = BookingStatus.CONFIRMED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        # арендодатель отклоняет бронь
        booking = self.get_object()

        if booking.listing.owner != request.user:
            return Response({'detail': 'Вы не владелец этого объявления.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != BookingStatus.PENDING:
            return Response({'detail': 'Отклонить можно только бронь в статусе pending.'},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = BookingStatus.REJECTED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        # переводит подтверждённую бронь в завершённую
        booking = self.get_object()

        if booking.listing.owner != request.user:
            return Response({'detail': 'Вы не владелец этого объявления.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != BookingStatus.CONFIRMED:
            return Response({'detail': 'Завершить можно только подтверждённую бронь.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not booking.is_finished:
            return Response({'detail': 'Завершить можно только после даты выезда.'},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = BookingStatus.COMPLETED
        booking.save()
        return Response(BookingSerializer(booking).data)