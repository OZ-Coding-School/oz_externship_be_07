from rest_framework import serializers
from apps.questions.models import QuestionCategories

# 어드민 카테고리 등록 시리얼라이저
class AdminCategoryCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source='id', read_only=True)

    parent_id = serializers.IntegerField(source='id', read_only=True)

    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=QuestionCategories.objects.all(),
        source='parent',
        required=False,
        allow_null=True
    )

    class Meta:
        model = QuestionCategories
        fields = [
            'category_id',
            'name',
            'category_type',
            'parent_id',
            'created_at'
        ]
    def validate(self, data):
        name = data.get('name')
        parent = data.get('parent')

        if QuestionCategories.objects.filter(name=name, parent=parent).exists():
            raise serializers.ValidationError("동일한 이름의 카테고리가 이미 존재합니다.")
        return data

    def to_representation(self, instance):
        ret = super(). to_representation(instance)
        if instance.created_at:
            ret['created_at'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
            return ret

