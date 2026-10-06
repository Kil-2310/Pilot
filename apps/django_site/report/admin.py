from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet

from .models import Report, ReportNote, ReportNotePhoto, ReportNoteVideo


class InlineReportNote(admin.StackedInline):
    """Инлайн класс дял записи в отчете"""

    model = ReportNote
    show_change_link = True


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Админка для ежедневного отчета"""

    list_display = ("date", "get_accompanied")
    inlines = [
        InlineReportNote,
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .prefetch_related("accompanied")
        )

    @admin.display(description="Отчет для сопровождаемого")
    def get_accompanied(self, obj: Report) -> str:
        return obj.accompanied.full_name


class InlineReportNotePhoto(admin.StackedInline):
    """Инлайн класс для фото в записи отчета"""

    model = ReportNotePhoto


class InlineReportNoteVideo(admin.StackedInline):
    """Инлайн класс для видео в записи отчета"""

    model = ReportNoteVideo


@admin.register(ReportNote)
class ReportNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "get_user", "created_at")
    inlines = [
        InlineReportNoteVideo,
        InlineReportNotePhoto,
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .prefetch_related("user")
        )

    @admin.display(description="Логин пилота")
    def get_user(self, obj: ReportNote) -> str:
        return obj.user.username
