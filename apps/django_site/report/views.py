from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import cached_property

from accompanied.models import Accompanied
from .utils import get_full_report
from .models import (
    Report,
    ReportNote,
    ReportNoteVideo,
    ReportNotePhoto,
)


class ReportListByAccompaniedView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Создание ежедневного отчета и получение списка из последних 3 отчетов"""

    template_name = "report/report-list.html"
    context_object_name = "reports"

    @cached_property
    def accompanied(self):
        return get_object_or_404(Accompanied, pk=self.kwargs["accompanied_pk"])

    def test_func(self):
        pilot = self.request.user.profile_pilot
        return pilot in self.accompanied.pilots.all()

    def get_queryset(self):
        Report.objects.get_or_create(
            accompanied=self.accompanied,
            date=timezone.now().date(),
        )

        return Report.objects.only(
            "date",
        ).filter(
            accompanied=self.accompanied
        )[:3]


class ReportDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Получение деталей отчета"""

    template_name = "report/report-detail.html"
    context_object_name = "report"

    def test_func(self):
        pilot = self.request.user.profile_pilot
        return pilot in self.get_object().accompanied.pilots.all()

    def get_queryset(self):
        return get_full_report()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now_date"] = timezone.now().date()
        return context


class ReportNoteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание заметки"""

    model = ReportNote
    template_name = "report/report-note-create.html"
    fields = (
        "title",
        "text",
    )

    @cached_property
    def report(self):
        return get_object_or_404(Report, pk=self.kwargs["pk"])

    def test_func(self):
        pilot = self.request.user.profile_pilot
        return pilot in self.report.accompanied.pilots.all()

    def form_valid(self, form):
        form.instance.report = self.report
        form.instance.user = self.request.user

        response = super().form_valid(form)

        for video in self.request.FILES.getlist("videos"):
            ReportNoteVideo.objects.create(report_note=self.object, video=video)

        for photo in self.request.FILES.getlist("photos"):
            ReportNotePhoto.objects.create(report_note=self.object, photo=photo)

        return response

    def get_success_url(self):
        return reverse("report:report_detail", kwargs={"pk": self.kwargs["pk"]})
