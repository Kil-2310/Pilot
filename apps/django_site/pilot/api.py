from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import ProfilePilot, Settlement
from .serializers import (
    GetProfilePilotSerializer,
    GetSettlementSerializer,
)


@extend_schema(
    tags=['pilot'],
    description='Получение всех пилотов',
)
class ProfilePilotListAPIView(ListAPIView):
    """Получение всех пилотов с фильтрацией по месту работы"""
    queryset = ProfilePilot.objects.get_active().get_only_fields().get_with_user()
    serializer_class = GetProfilePilotSerializer
    filterset_fields = ('settlements__name', )


@extend_schema(
    tags=['pilot'],
    description='Получение деталей пилота',
)
class ProfilePilotRetrieveAPIView(RetrieveAPIView):
    """Получение деталей пилота"""
    queryset = ProfilePilot.objects.get_active().get_only_fields().get_with_user()
    serializer_class = GetProfilePilotSerializer


@extend_schema(
    tags=['pilot'],
    description='Получение всех доступных населенных пунктов, в которых работают пилоты',
)
class SettlementListAPIView(ListAPIView):
    """Получение всех доступных населенных пунктов, в которых работают пилоты"""
    serializer_class = GetSettlementSerializer

    def get_queryset(self):
        return(
            Settlement.objects.filter(
                profile_pilot__user__is_active = True
            )
        )
