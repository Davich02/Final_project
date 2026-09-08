from django.db import models
from apps.users.models import User
from apps.core.models import TimeStampedModel
from djmoney.models.fields import MoneyField
# Create your models here.

class Listing(TimeStampedModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    location = models.CharField(max_length=200)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
    rooms = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    housing_type = models.CharField(max_length=50)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'





class ListingPhoto(TimeStampedModel):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='listings/photos/')

    class Meta:
        verbose_name = 'Фото объявления'
        verbose_name_plural = 'Фото объявлений'