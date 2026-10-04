from celery import Celery

from os import environ

environ.setdefault("DJANGO_SETTINGS_MODULE", "django_site.settings")
app = Celery("django_site")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
