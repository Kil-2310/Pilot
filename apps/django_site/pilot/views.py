from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse

from .models import ProfilePilot


class ProfilePilotDetailView(LoginRequiredMixin, DetailView):
    """Детали профиля пилота"""

    queryset = ProfilePilot.objects.prefetch_related(
        "accompanied", "settlements"
    ).select_related("user")

    template_name = "pilot/pilot-detail.html"
    context_object_name = "pilot"


class ProfilePilotUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля пилота"""

    model = ProfilePilot
    fields = ("description", "vk_name", "max_name", "telephone", "preview")
    template_name = "pilot/pilot-update.html"
    context_object_name = "pilot"

    def get_queryset(self):
        user = self.request.user
        return ProfilePilot.objects.filter(user=user).select_related("user")

    def get_success_url(self):
        return reverse("pilot:pilot_detail", kwargs={"pk": self.object.pk})
