from typing import Optional

from django.db.models import F, Q, QuerySet
from django.shortcuts import get_object_or_404

from apps.questions.models import QuestionCategories, Questions


# 질문 조회
class QuestionListService:
    @staticmethod
    def get_question_list(category_id: int | None = None, search_keyword: str | None = None) -> QuerySet[Questions]:
        queryset = Questions.objects.all()

        if category_id:
            category_ids = QuestionCategories.objects.filter(
                Q(id=category_id) | Q(parent_id=category_id) | Q(parent__parent_id=category_id)
            ).values_list("id", flat=True)
            queryset = queryset.filter(category_id__in=category_ids)

        if search_keyword:
            queryset = queryset.filter(title__contains=str(search_keyword))

        return queryset.order_by("-created_at")

    # 질문 상세 조회
    @staticmethod
    def get_question_detail(question_id: int) -> Questions:
        queryset = Questions.objects.select_related("category", "author").prefetch_related("images", "answers")

        question = get_object_or_404(queryset, id=question_id)

        Questions.objects.filter(id=question_id).update(view_count=F("view_count") + 1)
        question.refresh_from_db()

        return question
