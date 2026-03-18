from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.community.core.redis import RedisClient
from apps.community.signals.user_signal import (
    remove_user_search_data,
    stringify_user_tag,
)
from apps.users.models.models import User


class Command(BaseCommand):
    """
    수정시간 기준으로 1시간 전인 User 데이터 동기화
    """

    def handle(self, *args: Any, **kwargs: Any) -> None:
        one_hour_ago = timezone.now() - timedelta(hours=1)

        recently_updated_users = User.objects.filter(updated_at__gte=one_hour_ago)

        if not recently_updated_users.exists():
            self.stdout.write("동기화할 데이터가 없습니다.")
            return

        redis_conn = RedisClient.get_index(name="user_search")

        user_keys = [f"user_info:{user.id}" for user in recently_updated_users]
        old_data_list = redis_conn.mget(user_keys)
        user_with_old_data = zip(recently_updated_users, old_data_list)  # 같은 인덱스끼리 합침

        sync_user = 0
        with redis_conn.pipeline() as pipe:
            for user, old_data in user_with_old_data:
                if user.status in ["DEACTIVATED", "WITHDREW"]:
                    remove_user_search_data(user.id)
                    continue

                new_data = stringify_user_tag(user)
                info_key = f"user_info:{user.id}"

                if old_data:
                    pipe.zrem("user_search", old_data)
                pipe.zadd("user_search", {new_data: 0})
                pipe.set(info_key, new_data)
                sync_user += 1

            pipe.execute()
