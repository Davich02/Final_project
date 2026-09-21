from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'phone', 'is_staff', 'date_joined']
    list_filter = ['groups', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    exclude = ['password']  # хеш пароля в форме не показываем
    filter_horizontal = ['groups', 'user_permissions']
