import re
from typing import Any

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.community.models.comment_model import CommentTag, PostComment
from apps.users.models.models import User


class CommentService:
    @staticmethod
    def _update_tag_logic(comment_id: int, content: str, is_update: bool = True) -> None:
        """
        본문에서 닉네임을 추출하여 CommentTag를 갱신하는 로직
        """
        if is_update:
            CommentTag.objects.filter(comment_id=comment_id).delete()

        nicknames = re.findall(r"@([a-zA-Z0-9가-힣]+)", content)
        if not nicknames:
            return

        tagged_user_ids = User.objects.filter(nickname__in=set(nicknames)).values_list("id", flat=True)

        if tagged_user_ids:
            new_tags = [CommentTag(comment_id=comment_id, tagged_user_id=tagged_id) for tagged_id in tagged_user_ids]
            CommentTag.objects.bulk_create(new_tags)

    @staticmethod
    @transaction.atomic
    def create_comment_tags(post_id: int, author: Any, content: str) -> PostComment:
        """
        댓글과 태그 유저 저장
        """
        comment = PostComment.objects.create(post_id=post_id, author=author, content=content)

        CommentService._update_tag_logic(comment.id, content, False)

        return comment

    @staticmethod
    @transaction.atomic
    def update_comment_tags(comment_id: int, content: str) -> PostComment:
        """
        댓글과 태그 유저 수정
        """
        update_comment = PostComment.objects.filter(id=comment_id).update(content=content)
        if not update_comment:
            raise ValidationError("해당 댓글을 찾을 수 없습니다.")

        CommentService._update_tag_logic(comment_id, content, True)

        return PostComment.objects.get(id=comment_id)

    @staticmethod
    @transaction.atomic
    def delete_comment_tags(comment_id: int) -> None:
        """
        댓글과 태그 유저 삭제
        """
        CommentTag.objects.filter(comment_id=comment_id).delete()

        delete_comment = PostComment.objects.filter(id=comment_id).delete()

        if not delete_comment[0]:
            raise ValidationError("해당 댓글을 찾을 수 없습니다.")
