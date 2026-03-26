from typing import Any

from django.db.models import Q, QuerySet

from apps.questions.models import Questions


class AdminQuestionService:
    @staticmethod
    def get_question_list(
        page: int,
        size: int,
        search_keyword: str | None = None,
        category_id: int | None = None,
        answer_status: str | None = None,
        sort: str | None = "latest",
    ) -> dict[str, Any]:

        queryset: QuerySet[Questions] = Questions.objects.select_related(
            "author", "category", "category__parent"
        ).prefetch_related("answers")

        if search_keyword:
            queryset = queryset.filter(
                Q(title__icontains=search_keyword)
                | Q(content__icontains=search_keyword)
                | Q(author__nickname__icontains=search_keyword)
            )

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if answer_status == "answered":
            queryset = queryset.filter(answers__isnull=False).distinct()
        elif answer_status == "unanswered":
            queryset = queryset.filter(answers__isnull=True)

        if sort == "oldest":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        total_count = queryset.count()
        start = (page - 1) * size
        end = start + size
        questions = queryset[start:end]

        return {
            "page": page,
            "size": size,
            "search_keyword": search_keyword,
            "category_id": category_id,
            "answer_status": answer_status,
            "sort": sort,
        }
