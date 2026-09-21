from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'rating', 'comment', 'created_at']
    list_filter = ['rating']
    exclude = ['deleted_at']
