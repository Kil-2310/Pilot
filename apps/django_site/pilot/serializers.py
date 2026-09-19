from rest_framework import serializers
from .models import ProfilePilot


class BaseProfilePilotSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для профиля пилота"""
    class Meta:
        model = ProfilePilot
        fields = ('telephone','vk_name', 'max_name', 'description', )


class GetProfilePilotSerializer(BaseProfilePilotSerializer):
    """Получение профиля пилота"""
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta (BaseProfilePilotSerializer.Meta):
        fields = BaseProfilePilotSerializer.Meta.fields + ('first_name', 'last_name', 'email', )
