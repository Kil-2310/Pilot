from django.db import models
from django.contrib.auth.models import User


class ProfilePilot(models.Model):
    """Модель профиля пилота"""

    telephone = models.CharField(max_length=15, unique=True)
    max_name = models.CharField(max_length=50, blank=True)
    vk_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_pilot')

    def __str__(self):
        return f'{self.user.username} pilot'
