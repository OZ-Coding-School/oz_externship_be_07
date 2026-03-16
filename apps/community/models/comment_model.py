from django.db import models

from apps.core.models import TimeStampModel


class PostComment(TimeStampModel):
    """댓글"""

    author = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, verbose_name="작성자id")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, null=False, verbose_name="게시글id")
    content = models.CharField(max_length=300, null=False)

    def __str__(self) -> str:
        preview = (self.content[:12] + "...") if len(self.content) > 12 else self.content
        return f"{preview} - {self.author.nickname}"

    class Meta:
        db_table = "post_comments"
        verbose_name_plural = "게시글 댓글"
        indexes = [
            models.Index(fields=["post", "created_at"], name="idx_post_id_created_at"),
        ]


class CommentTag(TimeStampModel):
    """태그된 ID 저장"""

    tagged_user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, verbose_name="태그된 ID")
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=False, verbose_name="댓글")

    def __str__(self) -> str:
        return f"댓글#{self.comment_id} 태그: {self.tagged_user.nickname}"

    class Meta:
        db_table = "post_comment_tags"
        verbose_name_plural = "댓글 태그"
        indexes = [
            models.Index(fields=["tagged_user"], name="idx_tagged_user_id"),
        ]
        constraints = [models.UniqueConstraint(fields=["comment", "tagged_user"], name="unique_comment_tagged_user")]
