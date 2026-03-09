from django.db import models

# from apps.core.models import TimeStampedModel


class PostComment(models.Model):
    """댓글"""

    id = models.BigAutoField(primary_key=True)
    # author = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, verbose_name="작성자id")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, null=False, verbose_name="게시글id")
    content = models.CharField(max_length=300, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name="생성 일시")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="수정 일시")

    class Meta:
        db_table = "post_comment"
        indexes = [
            models.Index(fields=["post", "created_at"], name="idx_post_id_created_at"),
        ]


class CommentTag(models.Model):
    """태그된 ID 저장"""

    id = models.BigAutoField(primary_key=True)
    # tagged_user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, verbose_name="태그된 ID")
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=False, verbose_name="댓글")
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name="생성 일시")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="수정 일시")

    class Meta:
        db_table = "post_comment_tags"
        # indexes = [
        #     models.Index(fields=["tagged_user"], name="idx_tagged_user_id"),
        # ]
