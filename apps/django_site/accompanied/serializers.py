from rest_framework import serializers

from pilot.models import ProfilePilot
from .models import Accompanied


class PilotSerializer(serializers.ModelSerializer):
    """Сериализатор для пилотов"""
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = ProfilePilot
        fields = (
            'id', 'first_name', 'last_name', 'telephone',
            'max_name', 'vk_name', 'description',
        )


class BaseAccompaniedSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер для сопровождаемого"""
    preview = serializers.SerializerMethodField('get_preview')
    responsible_person_full_name = serializers.CharField(source='responsible_person.full_name')
    pilots = PilotSerializer(many=True)

    class Meta:
        model = Accompanied
        fields = (
            'id', 'preview', 'full_name', 'date_birth', 'description', 'health_problems',
            'tasks', 'responsible_person_full_name', 'pilots',
        )

    def get_preview(self, obj: Accompanied):
        if obj.preview:
            return obj.preview.url
        return 'No preview'


class GetAccompaniedSerializer(BaseAccompaniedSerializer):
    """Получение данных сопровождаемого"""
    class Meta(BaseAccompaniedSerializer.Meta):
        ...
