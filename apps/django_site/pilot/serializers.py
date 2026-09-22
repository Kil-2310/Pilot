from rest_framework import serializers

from .models import ProfilePilot, Settlement


class BaseProfilePilotSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для профиля пилота"""
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ProfilePilot
        fields = (
            'id', 'telephone','vk_name', 'max_name', 'description',
            'first_name', 'last_name', 'email',
        )


class GetProfilePilotSerializer(BaseProfilePilotSerializer):
    """Получение профиля пилота"""
    class Meta (BaseProfilePilotSerializer.Meta):
        ...


class BaseSettlementSerializer(serializers.ModelSerializer):
    """Базовый класс для населенных пунктов"""
    class Meta:
        model = Settlement
        fields = ('id', 'name', )


class GetSettlementSerializer(BaseSettlementSerializer):
    """Получение населенных пунктов"""
    class Meta (BaseSettlementSerializer.Meta):
        ...
