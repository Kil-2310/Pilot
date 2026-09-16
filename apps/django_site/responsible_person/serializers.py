from rest_framework import serializers
from .models import ResponsiblePerson


class BaseResponsiblePersonSerializer(serializers.ModelSerializer):
    """Базовый сериализатор с общими полями для ответственного лица"""
    class Meta:
        model = ResponsiblePerson
        fields = ('full_name', 'status', 'max_name', 'telephone', 'description')


class GetResponsiblePersonSerializer(BaseResponsiblePersonSerializer):
    """Получение данных ответственных лиц"""
    class Meta(BaseResponsiblePersonSerializer.Meta):
        pass


class PostResponsiblePersonSerializer(BaseResponsiblePersonSerializer):
    """Создание/обновление ответственных лиц"""
    class Meta(BaseResponsiblePersonSerializer.Meta):
        pass


class UpdateStatusResponsiblePersonSerializer(BaseResponsiblePersonSerializer):
    """Изменение статуса активного аккаунта на неактивный"""
    class Meta(BaseResponsiblePersonSerializer.Meta):
        fields = ('is_active', )
