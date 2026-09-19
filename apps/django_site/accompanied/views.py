from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from .models import Accompanied


class AccompaniedListView(LoginRequiredMixin, ListView):
    """Получение списка всех сопровождаемых"""
    queryset = (
        Accompanied.objects.filter(is_active=True)
        .only('preview', 'full_name', 'date_birth', 'description', )
    )

    template_name = 'accompanied/accompanied-list.html'
    context_object_name = 'accompanied_individuals'


class AccompaniedDetailView(LoginRequiredMixin, DetailView):
    """Получение деталей сопровождаемого"""
    queryset = (
        Accompanied.objects.filter(is_active=True)
        .only(
            'preview', 'full_name', 'date_birth', 'description', 'health_problems',
            'tasks', 'responsible_person__full_name'
        )
        .prefetch_related('pilots')
    )

    template_name = 'accompanied/accompanied-detail.html'
    context_object_name = 'accompanied'


class AccompaniedCreateView(LoginRequiredMixin, CreateView):
    """Создание нового сопровождаемого"""

    model = Accompanied
    fields = (
        'preview', 'full_name', 'date_birth', 'description',
        'health_problems', 'tasks', 'responsible_person',
    )

    template_name = 'accompanied/accompanied-create.html'
    success_url = reverse_lazy('accompanied:accompanied_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        pilot = self.request.user.profile_pilot
        self.object.pilots.add(pilot)
        return response


class AccompaniedUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление сопровождаемого"""
    model = Accompanied
    fields = (
        'preview', 'full_name', 'date_birth', 'description',
        'health_problems', 'tasks', 'pilots', 'responsible_person',
    )

    template_name = 'accompanied/accompanied-update.html'

    def get_success_url(self):
        return reverse('accompanied:accompanied_detail', kwargs={'pk': self.object.pk})


class AccompaniedRemovePilotView(LoginRequiredMixin, DeleteView):
    """Отвязка пилота от сопровождаемого (без удаления сопровождаемого)"""
    model = Accompanied
    template_name = 'accompanied/accompanied-delete.html'
    success_url = reverse_lazy('accompanied:accompanied_list')

    def form_valid(self, form):
        pilot = self.request.user.profile_pilot
        self.object.pilots.remove(pilot)
        return HttpResponseRedirect(self.get_success_url())
