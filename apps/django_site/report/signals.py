from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ReportNoteVideo, ReportNotePhoto
from .tasks import remove_file


@receiver(post_delete, sender=ReportNotePhoto)
def delete_photo_file(sender, instance: ReportNotePhoto, **kwargs):
    if not instance.photo:
        return
    file_name = instance.photo.name
    transaction.on_commit(lambda: remove_file.delay(file_name))


@receiver(post_delete, sender=ReportNoteVideo)
def delete_video_file(sender, instance: ReportNoteVideo, **kwargs):
    if not instance.video:
        return
    file_name = instance.video.name
    transaction.on_commit(lambda: remove_file.delay(file_name))
