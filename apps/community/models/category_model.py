from django.db import models
from django.db.models.functions import Lower
from apps.core.models import TimeStampModel


class PostCategory(TimeStampModel):
    """게시글 카테고리"""

    name = models.CharField(
        max_length=20,
        null=False,
        verbose_name="카테고리 이름",
        help_text="ex) 전체게시판, 공지사항, 자유게시판, 일상 공유, 개발 지식 공유, 취업 정보 공유, 프로젝트 구인",
    )
    status = models.BooleanField(
        default=True, null=False, verbose_name="카테고리 사용 여부", help_text="T: 사용, F: 미사용"
    )

    @staticmethod
    def normalize_name(name: str) -> str:
        return " ".join(name.split())

    def save(self, *args: object, **kwargs: object) -> None:
        if self.name:
            self.name = self.normalize_name(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} (#{self.pk})"

    class Meta:
        db_table = "post_categories"
        verbose_name = "게시글 카테고리"
        verbose_name_plural = "게시글 카테고리"
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_post_category_name",
            ),
        ]
