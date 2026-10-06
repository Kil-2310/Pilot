from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, ListView, UpdateView, CreateView
from django.urls import reverse_lazy, reverse

from .models import Accompanied


class AccompaniedListView(LoginRequiredMixin, ListView):
    """Получение списка всех сопровождаемых, привязанных к данному пилоту"""

    template_name = "accompanied/accompanied-list.html"
    context_object_name = "accompanied_individuals"

    def get_queryset(self):
        pilot = self.request.user.profile_pilot
        return (
            Accompanied.objects.get_active()
            .get_by_pilot(pilot)
            .only("preview", "full_name", "date_birth", "description")
        )


class AccompaniedDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Получение деталей сопровождаемого, привязанного к данному пилоту"""

    template_name = "accompanied/accompanied-detail.html"
    context_object_name = "accompanied"

    def test_func(self):
        pilot = self.request.user.profile_pilot
        return self.get_object().pilots.filter(pk=pilot.pk).exists()

    def get_queryset(self):
        return (
            Accompanied.objects.get_active()
            .only(
                "preview",
                "full_name",
                "date_birth",
                "description",
                "health_problems",
                "tasks",
                "responsible_person__full_name",
            )
            .prefetch_related("pilots")
        )


class AccompaniedCreateView(LoginRequiredMixin, CreateView):
    """Создание нового сопровождаемого"""

    model = Accompanied
    fields = (
        "preview",
        "full_name",
        "date_birth",
        "description",
        "health_problems",
        "tasks",
        "responsible_person",
    )

    template_name = "accompanied/accompanied-create.html"
    success_url = reverse_lazy("accompanied:accompanied_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        pilot = self.request.user.profile_pilot
        self.object.pilots.add(pilot)
        return response


class AccompaniedUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновление сопровождаемого"""

    model = Accompanied
    fields = (
        "preview",
        "full_name",
        "date_birth",
        "description",
        "health_problems",
        "tasks",
        "responsible_person",
    )

    def test_func(self):
        pilot = self.request.user.profile_pilot
        return self.get_object().pilots.filter(pk=pilot.pk).exists()

    template_name = "accompanied/accompanied-update.html"

    def get_success_url(self):
        return reverse("accompanied:accompanied_detail", kwargs={"pk": self.object.pk})
