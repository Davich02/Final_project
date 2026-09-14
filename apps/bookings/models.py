from django.db import models
from django.conf import settings
from apps.listings.models import Listing
from apps.core.models import TimeStampedModel, UniqueID, BookingStatus
from apps.core.managers import SoftDeleteManager
from django.utils import timezone
from django.core.exceptions import ValidationError


class Booking(UniqueID, TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='bookings')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')
    date_start = models.DateField()
    date_end = models.DateField()
    status = models.CharField(max_length=20, choices=BookingStatus, default=BookingStatus.PENDING)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    @property
    def is_finished(self):
        # проживание реально завершилось по датам, даже если статус ещё не обновили вручную
        return self.date_end < timezone.now().date()

    def clean(self):
        super().clean()
        # дата выезда не может быть раньше или равна дате заезда
        if self.date_start and self.date_end and self.date_end <= self.date_start:
            raise ValidationError({'date_end': 'Дата выезда должна быть позже даты заезда.'})

    def save(self, *args, **kwargs):
        # Django сам не запускает clean() при обычном save(), поэтому вызываем вручную
        self.full_clean()
        super().save(*args, **kwargs)

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
            models.Index(fields=['listing', 'date_start', 'date_end']),
        ]
