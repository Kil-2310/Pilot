from django.urls import path

from .api import (
    AccompaniedRetrieveAPIView,
)

app_name = "api_accompanied"

urlpatterns = [
    path(
        "persons-detail/<int:max_user_id>",
        AccompaniedRetrieveAPIView.as_view(),
        name="persons_detail",
    ),
]
