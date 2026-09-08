from django.db import models
from apps.bookings.models import Booking
from apps.core.models import TimeStampedModel
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Review(TimeStampedModel):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
