from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView

from .models import ResponsiblePerson
from .serializers import (
    GetResponsiblePersonSerializer,
    UpdateResponsiblePersonSerializer,
    CreateResponsiblePersonSerializer,
    UpdateStatusResponsiblePersonSerializer,
)


@extend_schema(
    tags=['responsible_person'],
    description='Получение деталей профиля',
)
class ResponsiblePersonDetailApiView(RetrieveAPIView):
    """Получение деталей профиля"""
    queryset = ResponsiblePerson.objects.get_only().get_active()
    serializer_class = GetResponsiblePersonSerializer
    lookup_field = 'max_user_id'


@extend_schema(
    tags=['responsible_person'],
    description='Создание ответственного лица',
)
class ResponsiblePersonCreateApiView(CreateAPIView):
    """Создание ответственного лица"""
    model = ResponsiblePerson
    serializer_class = CreateResponsiblePersonSerializer


@extend_schema(
    tags=['responsible_person'],
    description='Обновление ответственного лица',
)
class ResponsiblePersonUpdateApiView(UpdateAPIView):
    """Обновление ответственного лица"""
    queryset = ResponsiblePerson.objects.get_only().get_active()
    serializer_class = UpdateResponsiblePersonSerializer
    http_method_names = ['patch']
    lookup_field = 'max_user_id'


# @extend_schema(
#     tags=['responsible_person'],
#     description='Изменение статуса активного аккаунтка на неактивный и наоборот',
# )
# class ResponsiblePersonUpdateStatusApiView(UpdateAPIView):
#     """Изменение статуса активного аккаунтка на неактивный и наоборот"""
#     queryset = ResponsiblePerson.objects.get_only().get_active()
#     serializer_class = UpdateStatusResponsiblePersonSerializer
#     http_method_names = ['patch']
#     lookup_field = 'max_user_id'
