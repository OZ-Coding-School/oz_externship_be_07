import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("user_search")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "sync-user-search-every-hour": {
        "task": "apps.community.tasks.sync_user_search_task",
        "schedule": crontab(minute=0, hour="*"),
    },
}

app.autodiscover_tasks()
