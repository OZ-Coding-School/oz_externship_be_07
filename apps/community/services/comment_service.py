# apps/community/services/comment_service.py
from typing import List

from django.db import transaction

from apps.community.models import CommentTag, PostComment
from apps.users.models import User


class CommentService:
    @staticmethod
    @transaction.atomic
    def create_comment_tags(post_id: int, author: User, content: str, tagged_user_ids: List[int]) -> PostComment:
        """
        댓글과 태그 유저 저장
        """
        comment = PostComment.objects.create(post_id=post_id, author=author, content=content)

        if tagged_user_ids:
            for tagged_id in set(tagged_user_ids):
                CommentTag.objects.create(comment=comment, tagged_user_id=tagged_id)

        return comment
