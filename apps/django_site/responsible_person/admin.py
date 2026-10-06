from django.contrib import admin
from django.http import HttpRequest
from django.db.models.query import QuerySet

from .models import ResponsiblePerson
from accompanied.models import Accompanied


@admin.register(ResponsiblePerson)
class ResponsiblePersonAdmin(admin.ModelAdmin):
    """Модель админки для ответственного лица"""

    list_display = ("full_name", "get_accompanied_individuals")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .prefetch_related("accompanied_individuals")
        )

    @admin.display(description="Сопровождаемые лица")
    def get_accompanied_individuals(self, obj: ResponsiblePerson) -> str:
        return ", ".join(Accompanied.objects.filter(responsible_person=obj).values_list("full_name", flat=True))
