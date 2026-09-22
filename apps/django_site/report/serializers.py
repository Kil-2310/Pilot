from rest_framework import serializers

from .models import (
    Report,
    ReportNote,
    ReportNoteVideo,
    ReportNotePhoto
)


class ReportNoteVideoSerializer(serializers.ModelSerializer):
    """Сериализатор для видео"""
    video = serializers.SerializerMethodField('get_video')

    class Meta:
        model = ReportNoteVideo
        fields = ('video', 'created_at')

    def get_video(self, obj: ReportNoteVideo):
        return obj.video.url


class ReportNotePhotoSerializer(serializers.ModelSerializer):
    """Сериализатор для фото"""
    photo = serializers.SerializerMethodField('get_photo')

    class Meta:
        model = ReportNotePhoto
        fields = ('photo', 'created_at', )

    def get_photo(self, obj: ReportNotePhoto):
        return obj.photo.url


class ReportNoteSerializer(serializers.ModelSerializer):
    """Серилизатор для записей"""
    videos = ReportNoteVideoSerializer(many=True)
    photos = ReportNotePhotoSerializer(many=True)

    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = ReportNote
        fields = (
            'title', 'text', 'first_name', 'last_name',
            'videos', 'photos', 'created_at',
        )


class BaseReportSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для отчетов"""
    report_notes = ReportNoteSerializer(many=True)

    class Meta:
        model = Report
        fields = ('date', 'report_notes', )


class GetReportSerializer(BaseReportSerializer):
    """Получение всех отчетов"""
    class Meta(BaseReportSerializer.Meta):
        ...
