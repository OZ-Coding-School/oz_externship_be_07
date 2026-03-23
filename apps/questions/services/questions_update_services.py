from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.questions.models import QuestionCategories, QuestionImages, Questions
from apps.users.models.models import User


class QuestionUpdateService:
    @staticmethod
    @transaction.atomic
    def get_question_update(
        question_id: int,
        user: User,
        title: str | None,
        content: str | None,
        category_id: int | None = None,
        image_urls: list[str] | None = None,
    ) -> Questions:
        question = get_object_or_404(Questions, id=question_id)

        if question.author != user:
            raise PermissionDenied("본인이 작성한 질문만 수정 가능합니다.")

        if title is not None:
            question.title = title

        if content is not None:
            question.content = content

        if category_id is not None:
            category = get_object_or_404(QuestionCategories, id=category_id)
            question.category = category

        if image_urls is not None:
            question.images.all().delete()
            for url in image_urls:
                QuestionImages.objects.create(questions=question, img_url=url)

        question.save()
        return question
