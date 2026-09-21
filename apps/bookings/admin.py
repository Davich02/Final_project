from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['listing', 'tenant', 'date_start', 'date_end', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['listing__title', 'tenant__email']
    exclude = ['deleted_at']
