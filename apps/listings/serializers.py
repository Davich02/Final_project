from rest_framework import serializers
from .models import Listing, ListingPhoto


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'owner', 'title', 'description', 'location', 'price', 'rooms', 'housing_type', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['owner']

class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ['id', 'image', 'created_at', 'listing']
        read_only_fields = ['listing']