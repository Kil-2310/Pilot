from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse

from .models import ProfilePilot


class ProfilePilotDetailView(LoginRequiredMixin, DetailView):
    """Детали профиля пилота"""
    queryset = ProfilePilot.objects.get_active().get_only_fields().get_with_user()

    template_name = 'pilot/pilot-detail.html'
    context_object_name = 'pilot'


class ProfilePilotUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля пилота"""
    fields = ('description', 'vk_name', 'max_name', 'telephone', )
    queryset = ProfilePilot.objects.get_active().only(*fields)

    template_name = 'pilot/pilot-update.html'
    context_object_name = 'pilot'

    def get_success_url(self):
        return reverse('pilot:pilot_detail', kwargs={'pk': self.object.pk})
