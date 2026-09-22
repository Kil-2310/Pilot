from django.urls import path

from .api import ReportDetailByDateView


urlpatterns =  [
    path('accompanied-detail/<int:accompanied_id>/<str:date>/', ReportDetailByDateView.as_view()),
]
