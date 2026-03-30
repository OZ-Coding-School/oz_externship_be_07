from celery import shared_task  # type: ignore
from django.core.management import call_command

from apps.community.models.post_model import Post
from apps.community.services.post_service import   post_delete_sum, file_synchronization, post_file_save


@shared_task  # type: ignore
def sync_user_search_task() -> None:
    call_command("sync_user_search")

@shared_task
def file_delete_task(instance: Post) -> None:
    post_delete_sum(instance)

@shared_task
def file_synchronization_task(instance: Post) -> None:
    file_synchronization(instance)

@shared_task
def post_file_save_task(instance: Post) -> None:
    post_file_save(instance)