from celery import shared_task  # type: ignore
from django.core.management import call_command


@shared_task  # type: ignore
def sync_user_search_task() -> None:
    call_command("sync_user_search")
