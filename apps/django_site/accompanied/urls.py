from django.urls import path

from .views import (
    AccompaniedListView,
    AccompaniedDetailView,
    AccompaniedCreateView,
    AccompaniedRemovePilotView,
    AccompaniedUpdateView
)


app_name = 'accompanied'

# TODO изменить name для url remove-pilot/<int:pk>/
urlpatterns = [
    path('', AccompaniedListView.as_view(), name='accompanied_list'),
    path('detail/<int:pk>/', AccompaniedDetailView.as_view(), name='accompanied_detail'),
    path('create/', AccompaniedCreateView.as_view(), name='accompanied_create'),
    path('update/<int:pk>/', AccompaniedUpdateView.as_view(), name='accompanied_update'),
    path('remove-pilot/<int:pk>/', AccompaniedRemovePilotView.as_view(), name='accompanied_delete'),
]
