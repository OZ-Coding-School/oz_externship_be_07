from django.db import models


class PostCategory(models.Model):
    """게시글 카테고리"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=20,
        null=False,
        verbose_name="카테고리 이름",
        help_text="ex) 전체게시판, 공지사항, 자유게시판, 일상 공유, 개발 지식 공유, 취업 정보 공유, 프로젝트 구인",
    )
    status = models.BooleanField(
        default=True, null=False, verbose_name="카테고리 사용 여부", help_text="T: 사용, F: 미사용"
    )

    # created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name="생성 일시")
    # updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="수정 일시")

    class Meta:
        db_table = "post_category"
        verbose_name = "게시글 카테고리"
        indexes = [
            models.Index(fields=["id"], name="pk_post_category"),
        ]

    # def __str__(self):
    #     return self.name
