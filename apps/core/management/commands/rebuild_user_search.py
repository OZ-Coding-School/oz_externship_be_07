from typing import Any

from django.core.management.base import BaseCommand

from apps.community.core.redis import RedisClient
from apps.community.signals.user_signal import stringify_user_tag
from apps.users.models.models import User


class Command(BaseCommand):
    """
    DB기준으로 redis 데이터 재구축
    """

    def handle(self, *args: Any, **kwargs: Any) -> None:
        redis_conn = RedisClient.get_index(name="user_search")

        self.stdout.write("기존 데이터를 삭제 중")
        redis_conn.flushdb()

        not_active_users = ["DEACTIVATED", "WITHDREW"]
        active_users = User.objects.exclude(status__in=not_active_users)

        self.stdout.write(f"{active_users.count()}명의 유저 데이터 마이그레이션 중")

        with redis_conn.pipeline() as pipe:
            for user in active_users:
                data = stringify_user_tag(user)
                info_key = f"user_info:{user.id}"

                pipe.zadd("user_search", {data: 0})
                pipe.set(info_key, data)

                if len(pipe) >= 500:
                    pipe.execute()

            pipe.execute()

        self.stdout.write("성공적으로 데이터가 재구축되었습니다.")
