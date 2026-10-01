from django.urls import path

from .api import ReportDetailByDateView

app_name = "api_report"

urlpatterns = [
    path(
        "accompanied-detail/<int:accompanied_id>/<str:date>/",
        ReportDetailByDateView.as_view(),
        name="report_detail_by_date",
    ),
]
