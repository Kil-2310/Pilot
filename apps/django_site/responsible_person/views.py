from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView

from .models import ResponsiblePerson
from accompanied.models import Accompanied


class ResponsiblePersonDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Получение деталей ответственных лиц"""

    queryset = ResponsiblePerson.objects.get_active()

    template_name = "responsible_person/responsible-person-detail.html"
    context_object_name = "responsible_person"

    def test_func(self):
        pilot = self.request.user.profile_pilot
        return Accompanied.objects.filter(
            responsible_person=self.get_object(),
            pilots=pilot,
        ).exists()
