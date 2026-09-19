from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import ProfilePilot
from .serializers import (
    GetProfilePilotSerializer,
)


@extend_schema(
    tags=['pilot'],
    description='Получение всех пилотов',
)
class ProfilePilotListAPIView(ListAPIView):
    """Получение всех пилотов"""
    queryset = ProfilePilot.objects.get_active().get_only_fields().get_with_user()
    serializer_class = GetProfilePilotSerializer


extend_schema(
    tags=['pilot'],
    description='Получение деталей пилота',
)
class ProfilePilotRetrieveAPIView(RetrieveAPIView):
    """Получение деталей пилота"""
    queryset = ProfilePilot.objects.get_active().get_only_fields().get_with_user()
    serializer_class = GetProfilePilotSerializer
