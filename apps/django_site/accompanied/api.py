from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from pilot.models import ProfilePilot
from responsible_person.models import ResponsiblePerson
from .models import Accompanied
from .serializers import (
    GetAccompaniedSerializer,
)


class AccompaniedRetrieveAPIView(APIView):
    @extend_schema(
        tags=['accompanied'],
        description='Получение всех сопровождаемых, привязанных к ответственному лицу',
    )
    def get(self, request: Request, max_user_id: int) -> Response:
        """Получение всех сопровождаемых, привязанных к ответственному лицу"""
        responsible_person = get_object_or_404(ResponsiblePerson, max_user_id=max_user_id)

        accompanied_individuals = (
            Accompanied.objects
            .filter(responsible_person=responsible_person)
            .select_related('responsible_person')
            .prefetch_related(
                Prefetch(
                    'pilots',
                    queryset=ProfilePilot.objects.select_related('user')
                )
            )
        )

        return Response(
            GetAccompaniedSerializer(accompanied_individuals, many=True).data,
        )
