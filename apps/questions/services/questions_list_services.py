from typing import Optional

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.questions.models import Questions


# 질문 조회
class QuestionListService:
    @staticmethod
    def get_question_list(category_id: int | None = None, search_keyword: str | None = None) -> QuerySet[Questions]:
        queryset = Questions.objects.all()

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search_keyword:
            queryset = queryset.filter(title__contains=str(search_keyword))

        return queryset.order_by("-created_at")

    # 질문 상세 조회
    @staticmethod
    def get_question_detail(question_id: int) -> Questions:
        question = get_object_or_404(Questions, id=question_id)

        question.view_count = question.view_count + 1
        question.save()

        return question
