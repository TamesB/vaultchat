import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.conf.update(
    broker_url=os.environ.get("CELERY_BROKER_URL") or os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    result_backend=os.environ.get("CELERY_RESULT_BACKEND") or os.environ.get("REDIS_URL", "redis://redis:6379/0"),
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

