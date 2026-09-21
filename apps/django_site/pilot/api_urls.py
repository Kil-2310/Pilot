from django.urls import path

from .api import (
    ProfilePilotListAPIView,
    ProfilePilotRetrieveAPIView,
    SettlementListAPIView,
)

urlpatterns = [
    path('', ProfilePilotListAPIView.as_view()),
    path('detail/<int:pk>/', ProfilePilotRetrieveAPIView.as_view()),
    path('settlement/', SettlementListAPIView.as_view()),
]
