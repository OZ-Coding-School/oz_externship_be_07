from rest_framework.exceptions import NotFound

from apps.questions.models import Questions


# 관리자 질의응답 상세 조회
class AdminQuestionDetailService:
    @staticmethod
    def get_question_detail(question_id: int) -> Questions:
        try:
            return (
                Questions.objects.select_related("author", "category", "category__parent")
                .prefetch_related(
                    "images", "answers", "answers__author", "answers__comments", "answers__comments__author"
                )
                .get(id=question_id)
            )

        except Questions.DoesNotExist:
            raise NotFound({"error_detail": "존재하지 않는 질문입니다."})
