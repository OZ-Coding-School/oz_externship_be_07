from django.db import transaction

from apps.community.models.post_model import Post, PostLike
from apps.community.serializers.post_like_serializer import PostLikeResponseDTO


@transaction.atomic
def set_post_like(post_id: int, user_id: int, is_liked: bool) -> PostLikeResponseDTO:
    Post.objects.get(id=post_id, is_visible=True)

    post_like = PostLike.objects.select_for_update().filter(post_id=post_id, user_id=user_id).first()

    if post_like is None:
        PostLike.objects.create(
            post_id=post_id,
            user_id=user_id,
            is_liked=is_liked,
        )
    elif post_like.is_liked != is_liked:
        post_like.is_liked = is_liked
        post_like.save(update_fields=["is_liked", "updated_at"])

    like_count = PostLike.objects.filter(
        post_id=post_id,
        is_liked=True,
    ).count()

    return PostLikeResponseDTO(
        post_id=post_id,
        is_liked=is_liked,
        like_count=like_count,
    )
