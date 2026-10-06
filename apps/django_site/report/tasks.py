"""Celery задачи для удаления файлов."""

import logging
import os
from datetime import timedelta

from celery import shared_task
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.timezone import now

from .models import ReportNoteVideo, Report

logger = logging.getLogger(__name__)


@shared_task(max_retries=2)
def remove_file(file_name: str) -> None:
    if not file_name:
        return

    if default_storage.exists(file_name):
        default_storage.delete(file_name)
        logger.info("Удален файл с именем {}".format(file_name))


@shared_task(bind=True, max_retries=3)
def upload_video_to_s3(self, video_id, local_path, original_name):
    """Загрузка локального файла на S3"""
    video = ReportNoteVideo.objects.get(id=video_id)

    try:
        with open(local_path, "rb") as f:
            s3_key = f"videos/{video_id}_{original_name}"
            saved_path = default_storage.save(s3_key, File(f))

        video.video.name = saved_path
        video.status = "uploaded"
        video.save(update_fields=["video", "status"])

        os.remove(local_path)

    except Exception as exc:
        video.status = "failed"
        video.save(update_fields=["status"])
        # Повторная попытка через минуту
        raise self.retry(exc=exc, countdown=60)


@shared_task
def delete_old_reports():
    """Удаление отчетов старше 90 дней"""

    date_deleted = now() - timedelta(days=90)
    old_reports = Report.objects.filter(created_at__lt=date_deleted).prefetch_related(
        "accompanied"
    )

    logger.info(
        "Найдено {} устаревших отчетов, производится удаление".format(old_reports.count())
    )

    for report in old_reports:
        report.delete()
        logger.info(
            "Удален отчет, который принадлежит сопровождаемому {}.".format(
                report.accompanied.full_name
            )
        )
