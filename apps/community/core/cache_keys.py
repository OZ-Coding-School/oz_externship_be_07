def post_view_count_key(post_id: int) -> str:
    return f"community:post:{post_id}:views"


def post_viewer_key(post_id: int, viewer: str) -> str:
    return f"community:post:{post_id}:viewer:{viewer}"
