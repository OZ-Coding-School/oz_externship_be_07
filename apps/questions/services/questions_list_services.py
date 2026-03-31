from typing import Any

from django.db.models import Count, F, Q, QuerySet
from django.shortcuts import get_object_or_404

from apps.questions.models import QuestionCategories, Questions


# 질문 조회
class QuestionListService:
    @staticmethod
    def get_question_list(
        category_id: int | None = None,
        search_keyword: str | None = None,
        answer_status: str | None = None,
        sort_by: str = "latest",
    ) -> QuerySet[Questions]:
        queryset = Questions.objects.select_related("category", "author").annotate(answer_count=Count("answers")).all()

        if category_id:
            category_ids = QuestionCategories.objects.filter(
                Q(id=category_id) | Q(parent_id=category_id) | Q(parent__parent_id=category_id)
            ).values_list("id", flat=True)
            queryset = queryset.filter(category_id__in=category_ids)

        if search_keyword:
            queryset = queryset.filter(title__contains=str(search_keyword))

        if answer_status == "answered":
            queryset = queryset.filter(answer_count__gt=0)
        elif answer_status == "unanswered":
            queryset = queryset.filter(answer_count=0)

        if sort_by == "views":
            return queryset.order_by("-view_count", "-created_at")
        return queryset.order_by("-created_at")

    # 질문 상세 조회
    @staticmethod
    def get_question_detail(question_id: int, user: Any = None) -> Questions:
        queryset = Questions.objects.select_related("category", "author").prefetch_related("images", "answers")
        question = get_object_or_404(queryset, id=question_id)

        is_author = user and user.is_authenticated and question.author_id == user.id

        if not is_author:
            Questions.objects.filter(id=question_id).update(view_count=F("view_count") + 1)
            question.refresh_from_db()

        return question
