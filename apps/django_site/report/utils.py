from django.db.models import Prefetch
from django.db.models.query import QuerySet

from .models import (
    Report,
    ReportNote
)


def get_full_report() -> QuerySet:
    """Получение полного отчета: отчет, записи и медиа"""
    return (
        Report.objects
        .prefetch_related(
            Prefetch(
                'report_notes',
                queryset=(
                    ReportNote.objects
                    .prefetch_related('videos')
                    .prefetch_related('photos')
                )
            )
        )
    )
