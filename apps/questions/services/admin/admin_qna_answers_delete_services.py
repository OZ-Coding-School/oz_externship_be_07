from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.questions.models import AnswerComments, Answers


class AdminAnswerDeleteService:
    @transaction.atomic
    def delete_answer(self, answer_id: int) -> dict[str, Any]:
        answer = get_object_or_404(Answers, id=answer_id)

        deleted_comment_count = AnswerComments.objects.filter(answer=answer).count()
        answer.delete()

        return {
            "answer_id": answer_id,
            "deleted_comment_count": deleted_comment_count,
        }
