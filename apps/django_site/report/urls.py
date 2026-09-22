from django.urls import path

from .views import (
    ReportListByAccompaniedView,
    ReportDetailView,
    ReportNoteCreateView,
)


app_name = 'report'

urlpatterns =  [
    path('accompanied/<int:accompanied_pk>/', ReportListByAccompaniedView.as_view(), name='report_by_accompanied'),
    path('detail/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('detail/<int:pk>/note/create/', ReportNoteCreateView.as_view(), name='report_note_create'),
]
