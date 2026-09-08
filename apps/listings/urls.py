from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, ListingPhotoViewSet

router = DefaultRouter()
router.register(r'photos', ListingPhotoViewSet, basename='listing-photos')
router.register(r'', ListingViewSet, basename='listing')

urlpatterns = router.urls
