import uuid

from django.conf import settings
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
from .forms import ReportNoteMediaForm
from .tasks import upload_video_to_s3


class ReportListByAccompaniedView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Создание ежедневного отчета и получение списка из последних 3 отчетов"""

    template_name = "report/report-list.html"
    context_object_name = "reports"

    @cached_property
    def accompanied(self):
        return get_object_or_404(Accompanied, pk=self.kwargs["accompanied_pk"])

    def test_func(self):
        pilot = self.request.user.profile_pilot
        return self.accompanied.pilots.filter(pk=pilot.pk).exists()

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
        return self.get_object().accompanied.pilots.filter(pk=pilot.pk).exists()

    def get_queryset(self):
        return get_full_report()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now_date"] = timezone.now().date()
        return context


class ReportNoteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание заметки"""

    model = ReportNote
    template_name = "report/note-create.html"
    fields = (
        "title",
        "text",
    )

    @cached_property
    def report(self):
        return get_object_or_404(Report, pk=self.kwargs["pk"])

    def test_func(self):
        pilot = self.request.user.profile_pilot
        return self.report.accompanied.pilots.filter(pk=pilot.pk).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["media_form"] = ReportNoteMediaForm
        return context

    def form_valid(self, form):
        form.instance.report = self.report
        form.instance.user = self.request.user

        response = super().form_valid(form)

        video_file = self.request.FILES.get("video")
        if video_file:
            """
            Алгоритм сохранения видео:
            1. Видео сохраняется локально в папку TMP_DIR / tmp_name
            2. После сохранения Celery-задача отправляет видео в S3
            3. Видео удаляется из локальной папки
            """

            tmp_name = f"{uuid.uuid4()}_{video_file.name}"
            tmp_path = settings.TMP_DIR / tmp_name

            with open(tmp_path, "wb+") as f:
                for chunk in video_file.chunks():
                    f.write(chunk)

            video = ReportNoteVideo.objects.create(
                report_note=self.object, title=video_file.name
            )
            upload_video_to_s3.delay(video.pk, str(tmp_path), video_file.name)

        for i in range(1, 4):
            photo = self.request.FILES.get(f"photo_{i}")
            if photo:
                ReportNotePhoto.objects.create(
                    report_note=self.object, photo=photo, title=photo.name
                )

        return response

    def get_success_url(self):
        return reverse("report:report_detail", kwargs={"pk": self.kwargs["pk"]})
