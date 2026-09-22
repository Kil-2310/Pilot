from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from accompanied.models import Accompanied
from .serializers import GetReportSerializer
from .models import Report


extend_schema(
    tags=['report'],
    description='Получение отчета по сопровождаемому',
)
class ReportDetailByDateView(APIView):
    def get(self, request: Request, accompanied_id: int, date: str) -> Response:
        """Получение отчета по сопровождаемому"""
        if parse_date(date) is None:
            return Response(
                {'message': 'Неверный формат даты. Ожидается YYYY-MM-DD'},
                status=400,
            )

        accompanied = get_object_or_404(Accompanied, id=accompanied_id)
        report = Report.objects.filter(accompanied=accompanied, date=date).first()

        if not report:
            return Response(
                {'message': 'Пилот не создал отчет в этот день'},
                status=200,
            )

        return Response(
            GetReportSerializer(report).data,
        )
