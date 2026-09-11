from django.db import models
from apps.users.models import User
from apps.listings.models import Listing
from apps.core.models import TimeStampedModel, UniqueID
from apps.core.managers import SoftDeleteManager
from django.utils import timezone
from apps.core.models import BookingStatus
from django.core.exceptions import ValidationError

# Create your models here.

class Booking(UniqueID,TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    date_start = models.DateField()
    date_end = models.DateField()
    status = models.CharField(max_length=20, choices=BookingStatus, default=BookingStatus.PENDING)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        #ручной запуск 
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        #кастомная проверка дат бронирования
        super().clean()
        if self.date_start and self.date_end and self.date_end <= self.date_start:
            raise ValidationError({'date_end': 'Дата выезда должна быть позже даты заезда.'})

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def __str__(self):
        return f"{self.listing.title} ({self.date_start} — {self.date_end})"

    class Meta:
        ordering = ['-date_start']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['listing', 'date_start', 'date_end']),
        ]