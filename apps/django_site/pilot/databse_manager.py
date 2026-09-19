from django.db import models


class ProfilePilotQuerySet(models.QuerySet):
    def get_with_user(self):
        """Загрузка модели пользователя"""
        return self.select_related('user')

    def get_only_fields(self):
        """Получение определенных полей"""
        return (
            self.only(
                'telephone', 'user__first_name', 'user__last_name',
                'vk_name', 'max_name', 'description',
            )
        )

    def get_active(self):
        """Получение активных пользователей"""
        return self.filter(user__is_active=True)


class ProfilePilotManager(models.Manager.from_queryset(ProfilePilotQuerySet)):
    pass
