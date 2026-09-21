from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count
from drf_spectacular.utils import extend_schema, inline_serializer
from .models import SearchQuery, ListingView


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    # описываем ответ для swagger
    @extend_schema(responses=inline_serializer('PopularSearch', {
        'query': serializers.CharField(),
        'count': serializers.IntegerField(),
    }, many=True))
    @action(detail=False, methods=['get'], url_path='popular-searches')
    def popular_searches(self, request):
        popular = (
            SearchQuery.objects.values('query')
            .annotate(count=Count('query'))
            .order_by('-count')[:10]
        )
        return Response(list(popular))

    @extend_schema(responses=inline_serializer('PopularListing', {
        'listing__id': serializers.UUIDField(),
        'listing__title': serializers.CharField(),
        'views_count': serializers.IntegerField(),
    }, many=True))
    @action(detail=False, methods=['get'], url_path='popular-listings')
    def popular_listings(self, request):
        popular = (
            # без неактивных и удаленных
            ListingView.objects.filter(listing__is_active=True, listing__deleted_at__isnull=True)
            .values('listing__id', 'listing__title')
            .annotate(views_count=Count('id'))
            .order_by('-views_count')[:10]
        )
        return Response(list(popular))
