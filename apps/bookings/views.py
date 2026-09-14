from rest_framework import viewsets
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from apps.reviews.serializers import ReviewSerializer
from apps.core.models import BookingStatus


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # tenant подставляется сервером
        serializer.save(tenant=self.request.user)

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

        booking.status = BookingStatus.COMPLETED
        booking.save()
        return Response(BookingSerializer(booking).data)