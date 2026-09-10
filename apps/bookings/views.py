from django.shortcuts import render
from rest_framework import viewsets
from .models import Booking
from .serializers import BookingSerializer
from rest_framework.permissions import IsAuthenticated


# Create your views here.

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)
