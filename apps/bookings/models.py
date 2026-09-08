from django.db import models
from apps.users.models import User
from apps.listings.models import Listing
from apps.core.models import TimeStampedModel
# Create your models here.

class Booking(TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    date_start = models.DateField()
    date_end = models.DateField()
    status = models.CharField(max_length=50, default='pending')

    class Meta:
        ordering = ['-date_start']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'