from django import forms
from django_site.settings import MAX_VIDEO_SIZE, MAX_PHOTO_SIZE
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


def file_size_validator(max_size: int):
    def _validate(file):
        if file.size > max_size:
            raise ValidationError(
                f"Файл слишком большой, максимальный размер — {max_size // (1024 * 1024)} МБ."
            )

    return _validate


VIDEO_VALIDATORS = [
    FileExtensionValidator(["mp4", "avi", "mkv", "webm"]),
    file_size_validator(MAX_VIDEO_SIZE),
]

PHOTO_VALIDATORS = [
    FileExtensionValidator(["jpg", "jpeg", "png"]),
    file_size_validator(MAX_PHOTO_SIZE),
]


class ReportNoteMediaForm(forms.Form):
    """Форма с 1 видео и 3 фото"""

    video = forms.FileField(required=False, validators=VIDEO_VALIDATORS, label="Видео")

    photo_1 = forms.FileField(required=False, validators=PHOTO_VALIDATORS, label="Фото 1")
    photo_2 = forms.FileField(required=False, validators=PHOTO_VALIDATORS, label="Фото 2")
    photo_3 = forms.FileField(required=False, validators=PHOTO_VALIDATORS, label="Фото 3")
