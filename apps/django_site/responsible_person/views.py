from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from .models import ResponsiblePerson


class ResponsiblePersonDetailView(LoginRequiredMixin, DetailView):
    """Получение деталей ответственных лиц"""

    model = ResponsiblePerson
    template_name = "responsible_person/responsible-person-detail.html"
    context_object_name = "responsible_person"

    def get_queryset(self):
        pilot = self.request.user.profile_pilot
        return ResponsiblePerson.objects.filter(
            accompanied_individuals__pilots=pilot,
        ).distinct()
