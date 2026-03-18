from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.users.models.models import User
from apps.community.signals.user_signal import stringify_user_tag, remove_user_search_data
from django_redis import get_redis_connection  # type: ignore

class Command(BaseCommand):
    """
    수정시간 기준으로 1시간 전인 User 데이터 동기화
    """
    def handle(self, *args, **options) -> None:
        one_hour_ago = timezone.now() - timedelta(hours=1)

        recently_updated_users = User.objects.filter(updated_at__gte=one_hour_ago)

        if not recently_updated_users.exists():
            print("동기화할 데이터가 없습니다.")
            return

        redis_conn = get_redis_connection("user_search")

        for user in recently_updated_users:
            if user.status in ["DEACTIVATED", "WITHDREW"]:
                remove_user_search_data(user.id)
                continue

            new_data = stringify_user_tag(user)
            info_key = f"user_info:{user.id}"
            old_data = redis_conn.get(info_key)

            with redis_conn.pipeline() as pipe:
                if old_data:
                    pipe.zrem('user_search', old_data)
                pipe.zadd('user_search', {new_data: 0})
                pipe.set(info_key, new_data)
                pipe.execute()

        self.stdout.write(f"성공적으로 {recently_updated_users.count()}명의 데이터를 동기화했습니다.")