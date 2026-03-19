from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import F

from apps.community.core.cache import get_cache_client
from apps.community.core.cache_keys import post_view_count_pattern
from apps.community.models.post_model import Post


class Command(BaseCommand):
    help = "Redis에 누적된 게시글 조회수를 DB에 반영합니다."

    def handle(self, *args: Any, **options: Any) -> None:
        client = get_cache_client()
        keys = client.keys(post_view_count_pattern())

        updated_count = 0

        for raw_key in keys:
            key = raw_key.decode() if isinstance(raw_key, bytes) else raw_key
            value = client.get(key)
            if value is None:
                continue

            delta = int(value)
            if delta <= 0:
                continue

            try:
                post_id = int(key.split(":")[2])
            except (IndexError, ValueError):
                continue

            updated = Post.objects.filter(id=post_id).update(view_count=F("view_count") + delta)
            if updated:
                client.delete(key)
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"총 {updated_count}개의 게시글 조회수를 DB에 반영했습니다."))
