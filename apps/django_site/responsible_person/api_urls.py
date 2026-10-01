from django.urls import path

from .api import (
    ResponsiblePersonCreateApiView,
    ResponsiblePersonDetailApiView,
    ResponsiblePersonUpdateApiView,
)

app_name = "api_responsible_person"

urlpatterns = [
    path(
        "create/",
        ResponsiblePersonCreateApiView.as_view(),
        name="responsible_person_create",
    ),
    path(
        "detail/<int:max_user_id>/",
        ResponsiblePersonDetailApiView.as_view(),
        name="responsible_person_detail",
    ),
    path(
        "update/<int:max_user_id>/",
        ResponsiblePersonUpdateApiView.as_view(),
        name="responsible_person_update",
    ),
]
