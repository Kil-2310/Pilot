from django.db import models


class ResponsiblePersonQuerySet(models.QuerySet):
    def get_all(self):
        """Получение всех ответственных лиц"""
        return self.only('full_name', 'status', 'max_name', 'telephone', 'description', )


    def get_active(self):
        """Получение активных ответственных лиц"""
        return self.filter(is_active=True)


class ResponsiblePersonManager(models.Manager.from_queryset(ResponsiblePersonQuerySet)):
    pass
