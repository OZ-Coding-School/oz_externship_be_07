from typing import List, Optional

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404

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

        if user.is_authenticated == False:
            raise PermissionDenied("로그인이 필요한 서비스 입니다.")
        if user.role != "STUDENT":
            raise PermissionDenied("질문 등록은 수강생 권한이 필요합니다.")

        category = get_object_or_404(QuestionCategories, id=category_id)

        question = Questions.objects.create(author=user, category=category, title=title, content=content)
        if image_url_list:
            for url in image_url_list:
                QuestionImages.objects.create(questions=question, img_url=url)
        return question
