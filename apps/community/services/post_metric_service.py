from rest_framework.request import Request

from apps.community.core.cache import cache_get_int, cache_incr
from apps.community.core.cache_keys import post_view_count_key


def build_post_viewer_key(request: Request) -> str:
    if request.user.is_authenticated:
        return f"user:{request.user.id}"

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR", "anonymous")
    return f"ip:{ip}"


def increase_post_view_count(post_id: int, viewer_key: str) -> bool:
    cache_incr(post_view_count_key(post_id))
    return True


def get_merged_post_view_count(post_id: int, db_view_count: int) -> int:
    return db_view_count + cache_get_int(post_view_count_key(post_id), default=0)
