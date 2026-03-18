from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_redis import get_redis_connection

from apps.community.core.redis import RedisClient
from apps.users.models.models import User


def stringify_user_tag(user: User) -> str:
    """
    redis 저장 양식 설정
    """
    img_url = user.profile_img_url or ""

    return f"{user.nickname}:{user.id}:{img_url}"


def remove_user_search_data(user_id: int) -> None:
    redis_conn = get_redis_connection("user_search")
    info_key = f"user_info:{user_id}"
    old_data = RedisClient.get_string(info_key,"user_search")

    if old_data:
        with redis_conn as pipe:
            pipe.zrem("user_search", old_data)
            pipe.delete(info_key)
            pipe.execute()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_search(sender: Any, instance: User, created: Any, **kwargs: Any) -> None:
    def sync_redis() -> None:
        if getattr(instance, "status") in ["DEACTIVATED", "WITHDREW"]:
            remove_user_search_data(instance.id)
            return

        redis_conn = RedisClient.get_index("user_search")
        info_key = f"user_info:{instance.id}"
        new_data = stringify_user_tag(instance)
        old_data = RedisClient.get_string(info_key,"user_search")

        with redis_conn.pipeline() as pipe:
            if old_data:
                pipe.zrem("user_search", old_data)

            pipe.zadd("user_search", {new_data: 0})
            pipe.set(info_key, new_data)
            pipe.execute()

    transaction.on_commit(sync_redis)


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_user_search(sender: Any, instance: Any, **kwargs: Any) -> None:

    transaction.on_commit(lambda: remove_user_search_data(instance.id))
