from django.urls import path

from .views import (
    AccompaniedListView,
    AccompaniedDetailView,
    AccompaniedCreateView,
    AccompaniedDeleteView,
    AccompaniedUpdateView
)


app_name = 'accompanied'

urlpatterns = [
    path('', AccompaniedListView.as_view(), name='accompanied_list'),
    path('detail/<int:pk>', AccompaniedDetailView.as_view(), name='accompanied_detail'),
    path('create/', AccompaniedCreateView.as_view(), name='accompanied_create'),
    path('update/<int:pk>', AccompaniedUpdateView.as_view(), name='accompanied_update'),
    path('delete/<int:pk>', AccompaniedDeleteView.as_view(), name='accompanied_delete'),
]
