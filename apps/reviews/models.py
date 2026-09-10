from django.db import models
from apps.bookings.models import Booking
from apps.core.models import TimeStampedModel
from django.core.validators import MaxValueValidator, MinValueValidator
from apps.core.managers import SoftDeleteManager
from django.utils import timezone

# Create your models here.

class Review(TimeStampedModel):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

    objects = SoftDeleteManager()

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def __str__(self):
        return f"Review for {self.booking}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
