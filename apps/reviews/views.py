from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from .models import Review
from .serializers import ReviewSerializer


class ReviewFilter(filters.FilterSet):
    # отзывы по объявлению
    listing = filters.UUIDFilter(field_name='booking__listing')

    class Meta:
        model = Review
        fields = ['listing']


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.select_related('booking__tenant')
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter
