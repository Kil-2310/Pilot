from django.urls import path

from .api import (
    ProfilePilotListAPIView,
    ProfilePilotRetrieveAPIView,
)

urlpatterns = [
    path('', ProfilePilotListAPIView.as_view()),
    path('detail/<int:pk>/', ProfilePilotRetrieveAPIView.as_view()),
]
