from django_filters import rest_framework as filters
from .models import Listing



class ListingFilter(filters.FilterSet):
    # фильтрация цены и количества комнат
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte', label='Мин. цена')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte', label='Макс. цена')
    min_rooms = filters.NumberFilter(field_name='rooms', lookup_expr='gte', label='Мин. комнат')
    max_rooms = filters.NumberFilter(field_name='rooms', lookup_expr='lte', label='Макс. комнат')
    is_active = filters.BooleanFilter(field_name='is_active', label='Активно')
    country = filters.CharFilter(field_name='country', lookup_expr='exact', label='Страна')
    has_photos = filters.BooleanFilter(field_name='photos', method='filter_has_photos', label='Есть фото')


    def filter_has_photos(self, queryset, name, value):
        # кастом фильтр на просверку фото в обьявлении 
        if value:
            return queryset.filter(photos__isnull=False).distinct()
        return queryset.filter(photos__isnull=True)

    class Meta:
        model = Listing
        fields = ['city', 'housing_type', 'min_price', 'max_price', 'min_rooms', 'max_rooms',
                  'is_active', 'country', 'has_photos']