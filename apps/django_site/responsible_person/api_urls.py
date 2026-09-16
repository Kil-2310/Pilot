from django.urls import path

from .api import (
    ResponsiblePersonCreateApiView,
    ResponsiblePersonDetailApiView,
    ResponsiblePersonUpdateApiView,
    ResponsiblePersonUpdateStatusApiView,
)


urlpatterns = [
    path('create/', ResponsiblePersonCreateApiView.as_view()),
    path('detail/<int:pk>/', ResponsiblePersonDetailApiView.as_view()),
    path('update/<int:pk>/', ResponsiblePersonUpdateApiView.as_view()),
    path('update-status/<int:pk>/', ResponsiblePersonUpdateStatusApiView.as_view()),
]
