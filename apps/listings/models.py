from django.db import models
from apps.users.models import User
from apps.core.models import TimeStampedModel , UniqueID
from djmoney.models.fields import MoneyField
from apps.core.managers import SoftDeleteManager
from django.utils import timezone
from djmoney.models.validators import MinMoneyValidator
# Create your models here.

class Listing(UniqueID,TimeStampedModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    location = models.CharField(max_length=200)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR',
                       validators=[MinMoneyValidator(0)])
    rooms = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    housing_type = models.CharField(max_length=50)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['location']),
            models.Index(fields=['price']),
            models.Index(fields=['rooms']),
            models.Index(fields=['housing_type']),
        ]





class ListingPhoto(UniqueID,TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='listings/photos/')

    def __str__(self):
        return f"Photo for {self.listing.title}"

    class Meta:
        verbose_name = 'Фото объявления'
        verbose_name_plural = 'Фото объявлений'