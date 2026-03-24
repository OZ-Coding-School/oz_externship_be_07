from django.db.models import QuerySet

from apps.questions.models import QuestionCategories


class QuestionCategoryService:
    @staticmethod
    def get_category_type(instance: QuestionCategories | None) -> str:

        if instance is None:
            return "large"

        parent = instance.parent
        if parent is None:
            return "large"
        if parent.parent is None:
            return "medium"
        return "small"

    @staticmethod
    def get_user_category() -> QuerySet[QuestionCategories]:
        return QuestionCategories.objects.filter(parent__isnull=True).prefetch_related("children__children__children")

    @staticmethod
    def get_user_category_list() -> QuerySet[QuestionCategories]:
        return QuestionCategories.objects.all().select_related("parent__parent")
