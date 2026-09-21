from rest_framework import viewsets
from rest_framework.exceptions import ValidationError, PermissionDenied
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
from django.db.models import Q, Avg, Count
from apps.analytics.models import SearchQuery, ListingView


def visible_listings(user):
    # активные всем, неактивные только владельцу
    if user.is_authenticated:
        return Listing.objects.filter(Q(is_active=True) | Q(owner=user))
    return Listing.objects.filter(is_active=True)


class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    permission_classes = [IsLandlordOrReadOnly]
    pagination_class = ListingPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'average_rating']

    def get_queryset(self):
        # удаленные отзывы не считаем
        active_reviews = Q(bookings__review__isnull=False, bookings__review__deleted_at__isnull=True)
        return visible_listings(self.request.user).annotate(
            average_rating=Avg('bookings__review__rating', filter=active_reviews),
            reviews_count=Count('bookings__review', filter=active_reviews, distinct=True),
        ).prefetch_related('photos').order_by('-created_at')  # с annotate ordering из Meta не работает

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        # не удаляем если есть активные брони
        has_active_bookings = instance.bookings.filter(
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ).exists()
        if has_active_bookings:
            raise ValidationError(
                'У объявления есть активные бронирования. Отклоните или завершите их, '
                'либо снимите объявление с публикации (is_active=false).'
            )
        instance.delete()

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
        similar_listings = self.get_queryset().filter(
            city=listing.city,
            price__gte=listing.price.amount - price_range,
            price__lte=listing.price.amount + price_range,
            is_active=True
        ).exclude(id=listing.id)[:5]
        return Response(self.get_serializer(similar_listings, many=True).data)

    def list(self, request, *args, **kwargs):
        search_term = request.query_params.get('search', '').strip().lower()
        # пишем только на первой странице
        is_first_page = request.query_params.get('page', '1') == '1'
        if search_term and is_first_page:
            SearchQuery.objects.create(
                query=search_term,
                user=request.user if request.user.is_authenticated else None
            )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # свои просмотры не считаем
        if instance.owner != request.user:
            ListingView.objects.create(
                listing=instance,
                user=request.user if request.user.is_authenticated else None
            )
        return Response(self.get_serializer(instance).data)


class ListingPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = ListingPhotoSerializer
    permission_classes = [IsListingOwnerOrReadOnly]

    def get_queryset(self):
        return ListingPhoto.objects.filter(listing__in=visible_listings(self.request.user))

    def check_listing_owner(self, serializer):
        listing = serializer.validated_data.get('listing')
        if listing and listing.owner != self.request.user:
            raise PermissionDenied('Вы можете добавлять фото только к своим объявлениям.')

    def perform_create(self, serializer):
        self.check_listing_owner(serializer)
        serializer.save()

    def perform_update(self, serializer):
        self.check_listing_owner(serializer)
        serializer.save()
