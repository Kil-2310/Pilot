from django.urls import path

from .views import ResponsiblePersonDetailView


app_name = 'responsible_person'

urlpatterns = [
    path('detail/<int:pk>', ResponsiblePersonDetailView.as_view(), name='responsible_person_detail'),
]
