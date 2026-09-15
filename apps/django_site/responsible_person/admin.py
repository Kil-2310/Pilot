from django.contrib import admin

from .models import ResponsiblePerson


@admin.register(ResponsiblePerson)
class ResponsiblePersonAdmin(admin.ModelAdmin):
    """Модель админки для ответственного лица"""
    list_display = ('full_name', 'status', 'max_name', )
