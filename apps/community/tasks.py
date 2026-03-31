from celery import shared_task  # type: ignore
from django.core.management import call_command

from apps.community.services.post_service import (
    file_synchronization,
    post_file_delete,
    post_file_save,
)


@shared_task  # type: ignore
def sync_user_search_task() -> None:
    call_command("sync_user_search")


@shared_task  # type: ignore
def file_synchronization_task(post_id: int, post_content: str) -> None:
    file_synchronization(post_id, post_content)


@shared_task  # type: ignore
def post_file_save_task(post_id: int, post_content: str) -> None:
    post_file_save(post_id, post_content)
