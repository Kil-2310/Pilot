from django.urls import path

from .api import (
    ResponsiblePersonCreateApiView,
    ResponsiblePersonDetailApiView,
    ResponsiblePersonUpdateApiView,
    # ResponsiblePersonUpdateStatusApiView,
)


urlpatterns = [
    path('create/', ResponsiblePersonCreateApiView.as_view()),
    path('detail/<int:max_user_id>/', ResponsiblePersonDetailApiView.as_view()),
    path('update/<int:max_user_id>/', ResponsiblePersonUpdateApiView.as_view()),
    # path('update-status/<int:max_user_id>/', ResponsiblePersonUpdateStatusApiView.as_view()),
]
