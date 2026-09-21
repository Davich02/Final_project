from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Listing, ListingPhoto
from .serializers import ListingSerializer, ListingPhotoSerializer
from .permissions import IsLandlordOrReadOnly, IsListingOwnerOrReadOnly
from .filters import ListingFilter
from .pagination import ListingPagination
from apps.core.models import BookingStatus
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from django.db.models import Q
from apps.analytics.models import SearchQuery, ListingView







class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    permission_classes = [IsLandlordOrReadOnly]
    pagination_class = ListingPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Listing.objects.filter(Q(is_active=True) | Q(owner=user))
        return Listing.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], url_path='available')
    def available_dates(self, request, pk=None):
        # проверка свободных оконных дат (исключаем гадание в выборе )
        listing = self.get_object()
        booked_dates = listing.bookings.filter(
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ).values('date_start', 'date_end')
        return Response({'booked_ranges': list(booked_dates)})

    @action(detail=True, methods=['get'], url_path='similar')
    def similar_listing(self, request, pk=None):
        # похожие объявления: тот же город, цена ±20% от текущей
        listing = self.get_object()
        price_range = listing.price.amount * Decimal('0.2')
        similar_listings = Listing.objects.filter(
            city=listing.city,
            price__gte=listing.price.amount - price_range,
            price__lte=listing.price.amount + price_range,
            is_active=True
        ).exclude(id=listing.id)[:5]
        return Response(ListingSerializer(similar_listings, many=True).data)

    def list(self, request, *args, **kwargs):
        search_term = request.query_params.get('search')
        if search_term:
            SearchQuery.objects.create(
                query=search_term,
                user=request.user if request.user.is_authenticated else None
            )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ListingView.objects.create(
            listing=instance,
            user=request.user if request.user.is_authenticated else None
        )
        return super().retrieve(request, *args, **kwargs)




class ListingPhotoViewSet(viewsets.ModelViewSet):
    queryset = ListingPhoto.objects.all()
    serializer_class = ListingPhotoSerializer
    permission_classes = [IsListingOwnerOrReadOnly]

    def perform_create(self, serializer):
        listing_id = self.request.data.get('listing')
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            raise ValidationError({'listing': 'Объявление не найдено.'})

        if listing.owner != self.request.user:
            raise ValidationError({'listing': 'Вы можете добавлять фото только к своим объявлениям.'})

        serializer.save(listing=listing)