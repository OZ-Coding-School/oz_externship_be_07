def post_view_count_key(post_id: int) -> str:
    return f"community:post:{post_id}:views"


def post_view_count_pattern() -> str:
    return "community:post:*:views"


def post_viewer_key(post_id: int, viewer_key: str) -> str:
    return f"community:post:{post_id}:viewer:{viewer_key}"
