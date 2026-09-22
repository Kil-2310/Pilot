from django.contrib import admin

from .models import (
    Report,
    ReportNote,
    ReportNotePhoto,
    ReportNoteVideo
)

class InlineReportNote(admin.StackedInline):
    """Инлайн класс дял записи в отчете"""
    model = ReportNote
    show_change_link = True


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Админка для ежедневного отчета"""
    list_display = ('date', )
    inlines = [
        InlineReportNote,
    ]


class InlineReportNotePhoto(admin.StackedInline):
    """Инлайн класс для фото в записи отчета"""
    model = ReportNotePhoto


class InlineReportNoteVideo(admin.StackedInline):
    """Инлайн класс для видео в записи отчета"""
    model = ReportNoteVideo


@admin.register(ReportNote)
class ReportNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'report', 'created_at')
    inlines = [
        InlineReportNoteVideo,
        InlineReportNotePhoto,
    ]
