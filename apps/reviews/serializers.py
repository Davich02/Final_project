from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    listing = serializers.UUIDField(source='booking.listing_id', read_only=True)
    author = serializers.CharField(source='booking.tenant.first_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'booking', 'listing', 'author', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['booking']
