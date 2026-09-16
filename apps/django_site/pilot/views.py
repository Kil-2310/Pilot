from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse

from .models import ProfilePilot


class ProfilePilotDetailView(LoginRequiredMixin, DetailView):
    """Детали профиля пилота"""
    queryset = (
        ProfilePilot.objects.filter(user__is_active=True)
        .only('description', 'vk_name', 'max_name', 'telephone', 'user__username', )
    )

    template_name = 'pilot/pilot-detail.html'
    context_object_name = 'pilot'


class ProfilePilotUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля пилота"""
    fields = ('bio', 'vk_name', 'max_name', 'telephone', )
    queryset = (
        ProfilePilot.objects.filter(user__is_active=True)
        .only(*fields)
    )

    template_name = 'pilot/pilot-update.html'
    context_object_name = 'pilot'


    def get_success_url(self):
        """Вычисление корректного url для тукцщего пользователя"""
        return reverse('pilot:pilot_detail', kwargs={'pk': self.object.pk})
