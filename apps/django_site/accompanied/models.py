from django.db import models

from .databse_manager import AccompaniedManager
from pilot.models import ProfilePilot
from responsible_person.models import ResponsiblePerson


class Accompanied(models.Model):
    """Модель сопровождаемого"""

    class Meta:
        verbose_name='Профиль сопровождаемого'
        verbose_name_plural='Профили сопровождаемых'

    preview = models.ImageField(
        'Фото сопровождаемого',
        upload_to='accompanies/',
        blank=True,
        null=True,
    )
    full_name = models.CharField('ФИО', max_length=255)
    date_birth = models.DateField('Дата рождения')
    description = models.TextField('Описание сопровождаемого', max_length=500, blank=True)
    health_problems = models.TextField('Проблемы со здоровьем', max_length=800)
    tasks = models.TextField('Задачи пилота', max_length=800)
    is_active = models.BooleanField('Пользователь активен', default=True)

    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время последнего изменения', auto_now=True)

    pilots = models.ManyToManyField(
        ProfilePilot,
        verbose_name='Пилоты',
        related_name='accompanied',
        blank=True,
    )
    responsible_person = models.ForeignKey(
        ResponsiblePerson,
        verbose_name='Ответственное лицо',
        on_delete=models.SET_NULL,
        null=True,
    )

    objects = AccompaniedManager()

    def __str__(self):
        return f'Сопровождаемый: {self.full_name}'
