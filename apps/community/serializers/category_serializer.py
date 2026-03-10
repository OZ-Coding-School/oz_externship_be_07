from rest_framework import serializers

from apps.community.models import PostCategory

class PostCategoryListSpecSerializer(serializers.ModelSerializer[PostCategory]):
    """
    SPEC 응답용
    Fields:
        - id: 카테고리 ID
        - name: 카테고리 이름
    Usage:
        게시글 카테고리 목록 조회에 사용
    """
    class Meta:
        model = PostCategory
        fields = ["id", "name"]

class PostCategorySerializer(serializers.ModelSerializer[PostCategory]):
    """모델 기반 전체 필드"""
    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "created_at", "updated_at"]
        # read_only_fields = ["id", "created_at", "updated_at"] # 기본적으로 read-only처리되므로 생략가능, 단순 명시