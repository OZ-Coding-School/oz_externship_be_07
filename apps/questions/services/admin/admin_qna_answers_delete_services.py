from typing import Any

from django.db import transaction
from rest_framework.exceptions import (
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)

from apps.questions.models import AnswerComments, Answers


class AdminAnswerDeleteService:
    @staticmethod
    @transaction.atomic
    def delete_answer(user: Any, answer_id: int) -> dict[str, Any]:
        if not user or not user.is_authenticated:
            raise NotAuthenticated({"error_detail": "로그인이 필요합니다."})

        if not user.is_staff:
            raise PermissionDenied({"error_detail": "질의응답 삭제 권한이 없습니다."})

        if answer_id <= 0:
            raise ValidationError({"error_detail": "유효하지 않은 삭제 요청입니다."})

        try:
            answer = Answers.objects.get(id=answer_id)
        except Answers.DoesNotExist:
            raise NotFound({"error_detail": "삭제할 질문을 찾을 수 없습니다."})

        deleted_comment_count = AnswerComments.objects.filter(answer=answer).count()

        answer.delete()

        return {
            "answer_id": answer_id,
            "deleted_comment_count": deleted_comment_count,
        }
