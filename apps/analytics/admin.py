from django.contrib import admin
from .models import SearchQuery, ListingView


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'created_at']
    search_fields = ['query']


@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'created_at']
