from django.contrib import admin

from .models import ProfilePilot


@admin.register(ProfilePilot)
class ProfilePilotAdmin(admin.ModelAdmin):
    """Модель админки для профиля пилота"""
    list_display = ('telephone', 'max_name', 'vk_name')
