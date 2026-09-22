from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accompanied.models import Accompanied
from .models import (
    Report,
    ReportNote,
    ReportNoteVideo,
    ReportNotePhoto,
)


class ReportListByAccompaniedView(LoginRequiredMixin, ListView):
    """Создание ежедневного отчета и получение списка из последних 3 отчетов"""
    template_name = 'report/report-list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        user = self.request.user
        accompanied = get_object_or_404(Accompanied, pk=self.kwargs['accompanied_pk'])

        Report.objects.get_or_create(
            accompanied = accompanied,
            date = timezone.now().date(),
        )

        return (
            Report.objects
            .filter(
                accompanied__pilots = user.profile_pilot,
                accompanied = accompanied
            )
            [:3]
        )


class ReportDetailView(LoginRequiredMixin, DetailView):
    """Получение деталей отчета"""
    template_name = 'report/report-detail.html'
    context_object_name = 'report'

    def get_queryset(self):
        user = self.request.user

        return (
            Report.objects
            .filter(
                accompanied__pilots = user.profile_pilot,
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now_date'] = timezone.now().date()
        return context


class ReportNoteCreateView(LoginRequiredMixin, CreateView):
    """Создание заметки"""
    model = ReportNote
    template_name = 'report/report-note-create.html'
    fields = ('title', 'text', )

    def form_valid(self, form):
        user = self.request.user
        report = get_object_or_404(Report, pk=self.kwargs['pk'])

        form.instance.report = report
        form.instance.user = user

        response = super().form_valid(form)

        for video in self.request.FILES.getlist('videos'):
            ReportNoteVideo.objects.create(report_note=self.object, video=video)

        for photo in self.request.FILES.getlist('photos'):
            ReportNotePhoto.objects.create(report_note=self.object, photo=photo)

        return response

    def get_success_url(self):
        return reverse('report:report_detail', kwargs={'pk': self.kwargs['pk']})
