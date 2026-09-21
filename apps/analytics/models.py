from django.db import models
from django.conf import settings

# Create your models here.
class SearchQuery(models.Model):
    query = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='search_queries')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Поисковый запрос'
        verbose_name_plural = 'Поисковые запросы'


class ListingView(models.Model):
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='listing_views')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.listing.title} viewed at {self.created_at}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Просмотр объявления'
        verbose_name_plural = 'Просмотры объявлений'