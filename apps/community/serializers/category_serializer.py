from rest_framework import serializers

from apps.community.models.category_model import PostCategory

# SPEC 명세서와 전체모델이 차이가 있어 따로 분리


class PostCategoryListSpecSerializer(serializers.ModelSerializer[PostCategory]):
    """
    카테고리 목록 조회 SPEC 응답용 serializer
    Fields:
        - id: 카테고리 ID
        - name: 카테고리 이름
    용도:
        - 게시글 카테고리 목록 조회에 사용
        - 목록 렌더링에 필요한 최소 필드만 전달
    """

    class Meta:
        model = PostCategory
        fields = ["id", "name"]


class PostCategorySerializer(serializers.ModelSerializer[PostCategory]):
    """
    모델 기반 전체 필드 -> 카테고리 관리용 기본 serializer

    용도:
        - 카테고리 상세/관리 API에서 전체 필드 표현 시 사용
        - status, created_at, updated_at 확인이 필요한 관리자 페이지/도구 대응
    """

    class Meta:
        model = PostCategory
        fields = ["id", "name", "status", "created_at", "updated_at"]
        # read_only_fields = ["id", "created_at", "updated_at"] # 기본적으로 read-only처리되므로 생략가능, 단순 명시
