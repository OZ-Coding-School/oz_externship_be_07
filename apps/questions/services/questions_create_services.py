from typing import List, Optional

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.questions.models import QuestionCategories, QuestionImages, Questions
from apps.users.models.models import User


class QuestionCreateService:
    # 질문 등록
    @staticmethod
    @transaction.atomic
    def create_question(
        user: User,
        category_id: int,
        title: str,
        content: str,
        image_url_list: Optional[List[str]] = None,
    ) -> Questions:

        if not user.is_authenticated:
            raise PermissionDenied("로그인이 필요한 서비스 입니다.")
        if user.role != "STUDENT":
            raise PermissionDenied("질문 등록은 수강생 권한이 필요합니다.")

        category = QuestionCategories.objects.get(id=category_id)

        is_sub_category = (
            category.parent is not None and
            category.parent.parent is not None
        )

        if not is_sub_category:
            raise ValidationError("질문은 소분류 카테고리에 등록해야 합니다.")

        question = Questions.objects.create(author=user, category=category, title=title, content=content)
        if image_url_list:
            QuestionImages.objects.bulk_create(
                [QuestionImages(questions=question, img_url=url) for url in image_url_list]
            )
        return question
