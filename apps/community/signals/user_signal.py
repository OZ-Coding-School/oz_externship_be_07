from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_redis import get_redis_connection  # type: ignore


def get_redis_data(instance: Any) -> str:
    """
    redis 저장 양식 설정
    """
    img_url = instance.profile_img_url or ""

    return f"{instance.nickname}:{instance.id}:{img_url}"


def perform_redis_delete(user_id: int) -> None:
    redis_conn = get_redis_connection("user_search")
    info_key = f"user_info:{user_id}"
    old_data = redis_conn.get(info_key)

    with redis_conn.pipeline() as pipe:
        if old_data:
            pipe.zrem("user_search", old_data)
        pipe.delete(info_key)
        pipe.execute()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_search(sender: Any, instance: Any, created: Any, **kwargs: Any) -> None:
    def sync_redis() -> None:
        if getattr(instance, "status") == "DEACTIVATED":
            perform_redis_delete(instance.id)
            return

        redis_conn = get_redis_connection("user_search")
        info_key = f"user_info:{instance.id}"
        new_data = get_redis_data(instance)
        old_data = redis_conn.get(info_key)

        with redis_conn.pipeline() as pipe:
            if old_data:
                pipe.zrem("user_search", old_data)

            pipe.zadd("user_search", {new_data: 0})
            pipe.set(info_key, new_data)
            pipe.execute()

    transaction.on_commit(sync_redis)


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_user_search(sender: Any, instance: Any, **kwargs: Any) -> None:

    transaction.on_commit(lambda: perform_redis_delete(instance.id))
