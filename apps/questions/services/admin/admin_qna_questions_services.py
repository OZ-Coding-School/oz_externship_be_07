from typing import Any

from django.db.models import Q, QuerySet

from apps.questions.models import Questions


class AdminQuestionService:
    @staticmethod
    def get_question_list(page: int, size: int, search: str | None = None, sort: str | None = None) -> dict[str, Any]:
        queryset: QuerySet[Questions] = Questions.objects.select_related(
            "author", "category", "category__parent", "category__parent__parent"
        ).prefetch_related("answers")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search) | Q(author__nickname__icontains=search)
            )

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
            "total_count": total_count,
            "questions": questions,
        }
