from django.contrib import admin

from .models import Accompanied


@admin.register(Accompanied)
class AccompaniedAdmin(admin.ModelAdmin):
    """Модель админки для сопровождаемого"""

    list_display = ("full_name", "date_birth")
    search_fields = ("full_name",)
    search_help_text = "Введите ФИО полностью или частично"
