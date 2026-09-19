from django.db import models


class ResponsiblePersonQuerySet(models.QuerySet):
    def get_only(self):
        """Получение определенных полей"""
        return self.only('full_name', 'status', 'max_name', 'telephone', 'description', )

    def get_active(self):
        """Получение активных пользователей"""
        return self.filter(is_active=True)


class ResponsiblePersonManager(models.Manager.from_queryset(ResponsiblePersonQuerySet)):
    pass
