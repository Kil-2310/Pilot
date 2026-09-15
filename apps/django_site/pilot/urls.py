from django.urls import path

from .views import (
    ProfilePilotDetailView,
    ProfilePilotUpdateView,
)


app_name = 'pilot'

urlpatterns = [
    path('detail/<int:pk>', ProfilePilotDetailView.as_view(), name='pilot_detail'),
    path('update/<int:pk>', ProfilePilotUpdateView.as_view(), name='pilot_update'),
]
