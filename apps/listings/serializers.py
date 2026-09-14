from rest_framework import serializers
from .models import Listing, ListingPhoto


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'owner', 'title', 'description', 'country', 'city', 'district', 'street',
                  'house_number', 'price', 'rooms', 'housing_type', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['owner']


class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ['id', 'image', 'position', 'created_at', 'listing']
        read_only_fields = ['listing']