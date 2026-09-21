from django.contrib import admin
from .models import Listing, ListingPhoto


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    fields = ['image', 'position']
    extra = 0


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'city', 'district', 'price', 'rooms', 'housing_type', 'is_active', 'owner', 'created_at']
    list_filter = ['is_active', 'housing_type', 'city']
    search_fields = ['title', 'description', 'street']
    exclude = ['deleted_at']
    inlines = [ListingPhotoInline]


@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ['listing', 'position', 'created_at']
    exclude = ['deleted_at']
