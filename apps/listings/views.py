from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import Listing, ListingPhoto
from .serializers import ListingSerializer, ListingPhotoSerializer
from .permissions import IsLandlordOrReadOnly, IsListingOwnerOrReadOnly


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsLandlordOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ListingPhotoViewSet(viewsets.ModelViewSet):
    queryset = ListingPhoto.objects.all()
    serializer_class = ListingPhotoSerializer
    permission_classes = [IsListingOwnerOrReadOnly]

    def perform_create(self, serializer):
        listing_id = self.request.data.get('listing')
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            raise ValidationError({'listing': 'Объявление не найдено.'})

        if listing.owner != self.request.user:
            raise ValidationError({'listing': 'Вы можете добавлять фото только к своим объявлениям.'})

        serializer.save(listing=listing)