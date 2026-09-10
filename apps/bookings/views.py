from rest_framework import viewsets
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from apps.reviews.serializers import ReviewSerializer
from apps.core.models import BookingStatus

# Create your views here.

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)

    @action(detail=True, methods=['post'], url_path='review')
    def leave_review(self, request, pk=None):
        # валидация отзыва, можно оставить только после окончания броини ,только на свое бронирование 
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

