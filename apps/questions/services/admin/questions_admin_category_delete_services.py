from typing import Any

from django.db import transaction

from apps.questions.models import QuestionCategories, Questions


class AdminCategoryDeleteService:
    @staticmethod
    @transaction.atomic
    def execute_delete(target_category: QuestionCategories) -> dict[str, Any]:
        default_category, _ = QuestionCategories.objects.get_or_create(name="일반질문", defaults={"parent": None})

        def get_all_category_ids(category: QuestionCategories) -> list[int]:
            ids = [category.id]
            for child in category.children.all():
                ids.extend(get_all_category_ids(child))
            return ids

        target_ids = get_all_category_ids(target_category)

        questions_to_migrate = Questions.objects.filter(category_id__in=target_ids)
        migrated_count = questions_to_migrate.count()
        questions_to_migrate.update(category=default_category)

        category_type = "large"
        if target_category.parent:
            category_type = "medium"
            if target_category.parent.parent:
                category_type = "small"

        target_id = target_category.id
        target_category.delete()

        return {
            "category_id": target_id,
            "category_type": category_type,
            "migrated_question_count": migrated_count,
        }
