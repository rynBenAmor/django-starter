from django.contrib import admin

# Register your models here.
from .models import User
@admin.register(User)
class UserAmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'date_joined']