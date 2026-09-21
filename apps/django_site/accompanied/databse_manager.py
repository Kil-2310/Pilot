from django.db import models


class AccompaniedQuerySet(models.QuerySet):
    def get_active(self):
        """Получение активных сопровождаемых"""
        return self.filter(is_active=True)

    def get_by_pilot(self, pilot: 'ProfilePilot'):
        """Получение сопровождаемых, к которым текущий пользователь (пилот) имеет доступ"""
        return self.filter(pilots=pilot)


class AccompaniedManager(models.Manager.from_queryset(AccompaniedQuerySet)):
    pass
