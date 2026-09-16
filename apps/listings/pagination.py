from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Avg, Min, Max


class ListingPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        # вывод статистики цен по обтявлениям
        queryset = self.page.paginator.object_list
        stats = queryset.aggregate(avg=Avg('price'), min=Min('price'), max=Max('price'))
        average_price = round(stats['avg'], 2) if stats['avg'] else None

        return Response({
            'count': self.page.paginator.count,
            'price_stats': {
                'average_price': average_price,
                'min_price': stats['min'],
                'max_price': stats['max'],
            },
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })