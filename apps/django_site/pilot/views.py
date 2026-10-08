from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse

from .models import ProfilePilot


class ProfilePilotDetailView(LoginRequiredMixin, DetailView):
    """Детали профиля пилота"""

    queryset = ProfilePilot.objects.get_active().get_only_fields().get_with_user()

    template_name = "pilot/pilot-detail.html"
    context_object_name = "pilot"


class ProfilePilotUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновление профиля пилота"""

    model = ProfilePilot
    fields = ("description", "vk_name", "max_name", "telephone", "preview")
    template_name = "pilot/pilot-update.html"
    context_object_name = "pilot"

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return reverse("pilot:pilot_detail", kwargs={"pk": self.object.pk})
