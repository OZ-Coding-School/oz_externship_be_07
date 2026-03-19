from dataclasses import dataclass

from rest_framework import serializers


@dataclass(frozen=True)
class PostLikeResponseDTO:
    post_id: int
    is_liked: bool
    like_count: int


class PostLikeRequestSerializer(serializers.Serializer[dict[str, bool]]):
    is_liked = serializers.BooleanField()


class PostLikeResponseSerializer(serializers.Serializer[PostLikeResponseDTO]):
    detail = serializers.SerializerMethodField()
    post_id = serializers.IntegerField()
    is_liked = serializers.BooleanField()
    like_count = serializers.IntegerField()

    def get_detail(self, obj: PostLikeResponseDTO) -> str:
        return "좋아요 반영 완료" if obj.is_liked else "좋아요 취소 완료"
