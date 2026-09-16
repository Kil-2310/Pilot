from django.db import models

from .databse_manager import ResponsiblePersonManager


class ResponsiblePerson(models.Model):
    """Модель ответственного лица"""

    class Status(models.TextChoices):
        PARENT = 'parent', 'родитель'
        GUARDIAN = 'guardian', 'опекун'
        FRIEND = 'friend', 'друг'
        OTHER = 'other', 'другое'

    full_name = models.CharField('ФИО', max_length=255)
    status = models.CharField(
        'Статус ответственного лица по соотношению к сопровождаемому',
        max_length=50,
        choices=Status.choices,
        default=Status.OTHER,
    )
    max_name = models.CharField('Имя в MAX', max_length=50, unique=True)
    telephone = models.CharField('Номер телефона', max_length=15, unique=True)
    description = models.TextField('Описание',  max_length=500, blank=True)
    is_active = models.BooleanField('Активен', default=True)

    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время последнего изменения', auto_now=True)

    objects = ResponsiblePersonManager()

    def __str__(self):
        return f'Ответственное лицо {self.full_name}'
