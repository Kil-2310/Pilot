from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ReportNoteVideo, ReportNotePhoto


@receiver(post_delete, sender=ReportNoteVideo)
def delete_video_file(sender, instance: ReportNoteVideo, **kwargs):
    if instance.video:
        instance.video.delete(save=False)


@receiver(post_delete, sender=ReportNotePhoto)
def delete_photo_file(sender, instance: ReportNotePhoto, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)
