from rest_framework import serializers
from ...models import QuestionCategories

# 어드민 카테고리 목록 조회
class AdminQnaCategoryListSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source='id', read_only=True)
    category_type = serializers.SerializerMethodField()
    parent_category = serializers.CharField(source='parent.name', read_only=True, default=None)
    child_categories = serializers.SerializerMethodField()

    class Meta:
        model = QuestionCategories
        fields = [
            'category_id',
            'name',
            'category_type',
            'child_categories',
            'created_at',
        ]

    def get_category_type(self, obj):
        if not obj.parent:
            return "large"
        if not obj.parent.parent:
            return "medium"
        return "small"

    def get_child_categories(self, obj):
        return list(obj.childeren.values_list('name', flat=True))
