from django.urls import path

from .api import (
    AccompaniedRetrieveAPIView,
)


urlpatterns = [
    path('persons-detail/<int:max_user_id>', AccompaniedRetrieveAPIView.as_view()),
]
