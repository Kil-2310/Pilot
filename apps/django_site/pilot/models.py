from django.db import models
from django.contrib.auth.models import User

from .databse_manager import ProfilePilotManager


class ProfilePilot(models.Model):
    """Модель профиля пилота"""

    telephone = models.CharField('Телефон', max_length=15, unique=True)
    max_name = models.CharField('Имя в MAX', max_length=50, blank=True)
    vk_name = models.CharField('Имя в VK', max_length=50, blank=True)
    description = models.TextField('Описание', max_length=500, blank=True)

    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время последнего изменения', auto_now=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_pilot')

    objects = ProfilePilotManager()

    def __str__(self):
        return f'Пилот - {self.user.last_name} {self.user.first_name}'
