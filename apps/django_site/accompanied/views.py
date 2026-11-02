from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, UpdateView, CreateView
from django.urls import reverse_lazy, reverse
from django.db.models import Prefetch

from .models import Accompanied
from pilot.models import ProfilePilot
from responsible_person.models import ResponsiblePerson


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


class AccompaniedDetailView(LoginRequiredMixin, DetailView):
    """Получение деталей сопровождаемого, привязанного к данному пилоту"""

    model = Accompanied
    template_name = "accompanied/accompanied-detail.html"
    context_object_name = "accompanied"

    def get_queryset(self):
        pilot = self.request.user.profile_pilot
        return (
            Accompanied.objects.get_active()
            .get_by_pilot(pilot)
            .select_related("responsible_person")
            .prefetch_related(
                Prefetch("pilots", queryset=(ProfilePilot.objects.select_related("user")))
            )
        )


class AccompaniedCreateView(LoginRequiredMixin, CreateView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["responsible_person"] = ResponsiblePerson.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        pilot = self.request.user.profile_pilot
        self.object.pilots.add(pilot)
        return response


class AccompaniedUpdateView(LoginRequiredMixin, UpdateView):
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
    template_name = "accompanied/accompanied-update.html"

    def get_success_url(self):
        return reverse("accompanied:accompanied_detail", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        pilot = self.request.user.profile_pilot
        return Accompanied.objects.select_related("responsible_person").filter(
            pilots=pilot
        )
