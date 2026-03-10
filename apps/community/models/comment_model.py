from django.db import models

from apps.core.models import TimeStampModel


class PostComment(TimeStampModel):
    """댓글"""

    author = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, verbose_name="작성자id")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, null=False, verbose_name="게시글id")
    content = models.CharField(max_length=300, null=False)

    class Meta:
        db_table = "post_comments"
        indexes = [
            models.Index(fields=["post", "created_at"], name="idx_post_id_created_at"),
        ]


class CommentTag(TimeStampModel):
    """태그된 ID 저장"""

    tagged_user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, verbose_name="태그된 ID")
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=False, verbose_name="댓글")

    class Meta:
        db_table = "post_comment_tags"
        indexes = [
            models.Index(fields=["tagged_user"], name="idx_tagged_user_id"),
        ]
        constraints = [models.UniqueConstraint(fields=["comment", "tagged_user"], name="unique_comment_tagged_user")]
