from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]