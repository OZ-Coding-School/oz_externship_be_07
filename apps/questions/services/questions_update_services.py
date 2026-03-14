from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.questions.models import Questions
from apps.users.models.models import User


# 질문 수정
class QuestionUpdateService:
    @staticmethod
    def get_question_update(question_id: int, user: User, title: str, content: str) -> Questions:
        question = get_object_or_404(Questions, id=question_id)

        if question.author != user:
            raise PermissionDenied("본인이 작성한 질문만 수정할 수 있습니다.")

        question.title = title
        question.content = content

        question.save()
        return question
