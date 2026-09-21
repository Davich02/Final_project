from rest_framework import serializers
from .models import Listing, ListingPhoto


class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ['id', 'image', 'position', 'created_at', 'listing']


class ListingSerializer(serializers.ModelSerializer):
    photos = ListingPhotoSerializer(many=True, read_only=True)
    # считаются в get_queryset
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['id', 'owner', 'title', 'description', 'country', 'city', 'district', 'street',
                  'house_number', 'price', 'rooms', 'housing_type', 'is_active',
                  'average_rating', 'reviews_count', 'photos',
                  'created_at', 'updated_at']
        read_only_fields = ['owner']

    # getattr потому что у нового объявления этих полей нет
    def get_average_rating(self, obj) -> float | None:
        rating = getattr(obj, 'average_rating', None)
        return round(float(rating), 1) if rating is not None else None

    def get_reviews_count(self, obj) -> int:
        return getattr(obj, 'reviews_count', 0)
