from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing, ListingPhoto
from .serializers import ListingSerializer,ListingPhotoSerializer
from .permissions import IsLandlordOrReadOnly
# Create your views here.

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsLandlordOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ListingPhotoViewSet(viewsets.ModelViewSet):
    queryset = ListingPhoto.objects.all()
    serializer_class = ListingPhotoSerializer