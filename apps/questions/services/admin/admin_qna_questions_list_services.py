from rest_framework.exceptions import NotFound

from apps.questions.models import Questions


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
            raise NotFound("해당 질문을 찾을 수 없습니다.")
