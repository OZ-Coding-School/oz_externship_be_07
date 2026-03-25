from typing import Optional

from django.db.models import QuerySet

from ...models import QuestionCategories


# 카테고리 목록 조회
class AdminQnaCategoryListService:
    @staticmethod
    def get_category_list(
        search_keyword: Optional[str] = None, category_type: Optional[str] = None
    ) -> QuerySet[QuestionCategories]:
        queryset = QuestionCategories.objects.all().select_related("parent").prefetch_related("children")

        if search_keyword:
            queryset = queryset.filter(name__icontains=search_keyword)

        if category_type:
            if category_type == "large":
                queryset = queryset.filter(parent__isnull=True)
            elif category_type == "medium":
                queryset = queryset.filter(parent__isnull=False, parent__parent__isnull=True)
            elif category_type == "small":
                queryset = queryset.filter(parent__parent__isnull=False)

        return queryset.order_by("-created_at")
