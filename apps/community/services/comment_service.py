# apps/community/services/comment_service.py
from typing import Any, List

from django.db import transaction

from apps.community.models.comment_model import CommentTag, PostComment


class CommentService:
    @staticmethod
    @transaction.atomic
    def create_comment_tags(post_id: int, author: Any, content: str, tagged_user_ids: List[int]) -> PostComment:
        """
        댓글과 태그 유저 저장
        """
        comment = PostComment.objects.create(post_id=post_id, author=author, content=content)

        if tagged_user_ids:
            tags = [
                CommentTag(comment=comment, tagged_user_id=tagged_id)
                for tagged_id in set(tagged_user_ids)
            ]

            CommentTag.objects.bulk_create(tags)

        return comment
