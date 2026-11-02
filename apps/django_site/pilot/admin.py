from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ProfilePilot, Settlement

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Перпеопределение базовой мадели админки User"""

    list_display = (
        "username",
        "email",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(groups__name="Pilots")


@admin.register(ProfilePilot)
class ProfilePilotAdmin(admin.ModelAdmin):
    """Модель админки для профиля пилота"""

    list_display = (
        "get_user_username",
        "get_user_first_and_last_names",
        "telephone",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")

    @admin.display(description="Фамилия и имя пилота")
    def get_user_first_and_last_names(self, obj: ProfilePilot) -> str:
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        return f"{last_name} {first_name}"

    @admin.display(description="Логин пилота")
    def get_user_username(self, obj: ProfilePilot) -> str:
        return obj.user.username


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    """Модель админки для населенных пунктов"""

    list_display = ("name",)
    search_fields = ("name",)
    search_help_text = "Введите название населенного пункта полностью или частично"
