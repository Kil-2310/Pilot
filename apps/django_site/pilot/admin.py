from django.contrib import admin

from .models import ProfilePilot, Settlement


@admin.register(ProfilePilot)
class ProfilePilotAdmin(admin.ModelAdmin):
    """Модель админки для профиля пилота"""
    list_display = ('telephone', 'max_name', 'vk_name')


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    """Модель админки для населенных пунктов"""
    list_display = ('name', )
