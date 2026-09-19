from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from .models import ResponsiblePerson


class ResponsiblePersonDetailView(LoginRequiredMixin, DetailView):
    """Получение деталей ответственных лиц"""
    queryset = ResponsiblePerson.objects.get_only().get_active()

    template_name = 'responsible_person/responsible-person-detail.html'
    context_object_name = 'responsible_person'
