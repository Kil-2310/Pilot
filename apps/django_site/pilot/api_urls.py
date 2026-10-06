from django.urls import path

from .api import (
    ProfilePilotListAPIView,
    ProfilePilotRetrieveAPIView,
    SettlementListAPIView,
)

app_name = "api_pilot"

urlpatterns = [
    path("", ProfilePilotListAPIView.as_view(), name="pilot_list"),
    path("detail/<int:pk>/", ProfilePilotRetrieveAPIView.as_view(), name="pilot_detail"),
    path("settlement/", SettlementListAPIView.as_view(), name="settlement_list"),
]
