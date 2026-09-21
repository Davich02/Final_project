from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count
from .models import SearchQuery, ListingView


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='popular-searches')
    def popular_searches(self, request):
        popular = (
            SearchQuery.objects.values('query')
            .annotate(count=Count('query'))
            .order_by('-count')[:10]
        )
        return Response(list(popular))

    @action(detail=False, methods=['get'], url_path='popular-listings')
    def popular_listings(self, request):
        popular = (
            ListingView.objects.values('listing__id', 'listing__title')
            .annotate(views_count=Count('id'))
            .order_by('-views_count')[:10]
        )
        return Response(list(popular))