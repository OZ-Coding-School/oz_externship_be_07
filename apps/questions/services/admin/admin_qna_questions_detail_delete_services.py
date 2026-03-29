from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.questions.models import AnswerComments, Answers, Questions


class AdminQuestionDeleteService:
    @transaction.atomic
    def delete_question(self, question_id: int) -> dict[str, Any]:
        question = get_object_or_404(Questions, id=question_id)

        answers_qs = Answers.objects.filter(questions=question)

        deleted_answer_count = answers_qs.count()
        deleted_comment_count = AnswerComments.objects.filter(answer__in=answers_qs).count()

        question.delete()

        return {
            "question_id": question_id,
            "deleted_answer_count": deleted_answer_count,
            "deleted_comment_count": deleted_comment_count,
        }
