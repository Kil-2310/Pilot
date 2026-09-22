from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

from accompanied.models import Accompanied


class Report(models.Model):
    """Модель отчета за день"""

    class Meta:
        verbose_name='Отчет'
        verbose_name_plural='Отчеты'

    date = models.DateField('Дата', default=timezone.localdate)

    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время последнего изменения', auto_now=True)

    accompanied = models.ForeignKey(
        Accompanied,
        verbose_name='Отчет для сопровождаемого',
        on_delete=models.CASCADE,
        related_name='reports',
    )

    def __str__(self):
        return f'Отчет {self.date} для сопровождаемого {self.accompanied.full_name}'


class ReportNote(models.Model):
    """Модель записи в отчете"""

    class Meta:
        verbose_name = 'Запись отчета'
        verbose_name_plural = 'Записи отчетов'

    title = models.CharField('Название отчета', max_length=255)
    text = models.TextField('Текст записи в отчете', blank=True)

    created_at = models.DateTimeField('Время создания', auto_now_add=True)

    report = models.ForeignKey(
        Report,
        verbose_name='Отчет',
        on_delete=models.CASCADE,
        related_name='report_notes',
        blank=True,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Автор отчета',
        on_delete=models.CASCADE,
        related_name='report_notes',
        blank=True,
    )

    def __str__(self):
        return f'Запись в отчете: {self.title}'


class ReportNoteVideo(models.Model):
    """Модель для видео в отчете"""

    class Meta:
        verbose_name = 'Видео запись'
        verbose_name_plural = 'Видео записи'

    video = models.FileField(
        upload_to='report_videos/%Y/%m/%d/',
        validators=[FileExtensionValidator(
            allowed_extensions=['mp4', 'mov', 'avi', 'webm']
        )],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    report_note = models.ForeignKey(
        ReportNote,
        verbose_name='Видео в записи',
        on_delete=models.CASCADE,
        related_name='videos',
    )

    def __str__(self):
        return f'Видео для отчета {self.report_note.title}'


class ReportNotePhoto(models.Model):
    """Модель для фото в отчете"""

    class Meta:
        verbose_name = 'Фото записи'
        verbose_name_plural = 'Фотографии записей'

    photo = models.FileField(
        upload_to='report_photo/%Y/%m/%d/',
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp']
        )],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    report_note = models.ForeignKey(
        ReportNote,
        verbose_name='Фото в записи',
        on_delete=models.CASCADE,
        related_name='photos',
    )

    def __str__(self):
        return f'Фото для отчета {self.report_note.title}'
