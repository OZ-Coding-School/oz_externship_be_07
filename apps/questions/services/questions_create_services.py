from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.questions.models import QuestionCategories, QuestionImages, Questions
from apps.users.choices import UserRole
from apps.users.models.models import User


class QuestionCreateService:
    @staticmethod
    @transaction.atomic
    def create_question(
        user: User,
        category_id: int,
        title: str,
        content: str,
        image_url_list: list[str] | None = None,
    ) -> Questions:

        # 수강생과 어드민 권한
        allowed_roles = [UserRole.STUDENT, UserRole.ADMIN]

        # 수강생 이상 권한은 조회 가능
        if user.role not in allowed_roles:
            raise PermissionDenied("질문 등록 권한이 없습니다.")

        category = QuestionCategories.objects.get(id=category_id)

        is_sub_category = category.parent is not None and category.parent.parent is not None

        if not is_sub_category:
            raise ValidationError("질문은 소분류 카테고리에 등록해야 합니다.")

        question = Questions.objects.create(author=user, category=category, title=title, content=content)
        if image_url_list:
            QuestionImages.objects.bulk_create(
                [QuestionImages(questions=question, img_url=url) for url in image_url_list]
            )
        return question
