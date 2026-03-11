from typing import Any, Dict, List, Optional

from rest_framework import serializers

from .models import AnswerComments, AnswerImages, Answers, QuestionAiAnswers
from .questions_serializer import AuthorSerializer


# 1. AI 답변
class QuestionAiAnswerSerializer(serializers.ModelSerializer[QuestionAiAnswers]):
    class Meta:
        model = QuestionAiAnswers
        # AI 답변 내용, 사용된 모델명, 생성 시간을 포함합니다.
        fields = ["output", "using_model", "created_at"]


# 2. 답변 이미지
class AnswerImagesSerializer(serializers.ModelSerializer[AnswerImages]):
    class Meta:
        model = AnswerImages
        # 이미지 고유ID, 프론트에서 사용할 img_url
        fields = ["id", "img_url"]


# 3. 답변 댓글
class AnswerCommentSerializer(serializers.ModelSerializer[AnswerComments]):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = AnswerComments
        fields = ["id", "author", "content", "created_at"]


# 4. 메인 답변
class AnswersSerializer(serializers.ModelSerializer[Answers]):
    author = AuthorSerializer(read_only=True)
    comments = AnswerCommentSerializer(many=True, read_only=True)
    images = AnswerImagesSerializer(many=True, read_only=True)

    # 질문 등록시 여러 이미지 URL받기 리스트
    uploaded_images: serializers.ListField = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Answers
        # 상세 조회 시 필요한 모든 정보
        fields = [
            "id",
            "questions",
            "author",
            "content",
            "is_adopted",
            "comments",
            "images",
            "uploaded_images",
            "created_at",
            "updated_at",
        ]

    # 답변 생성 (이미지동시저장)
    def create(self, validated_data: Dict[str, Any]) -> Answers:
        # 이미지 리스트 추출
        image_urls: List[str] = validated_data.pop("uploaded_images", [])
        # 답변을 DB에 저장
        answer = Answers.objects.create(**validated_data)
        # 추출한 url들을 모델과 연결해 생성
        for url in image_urls:
            AnswerImages.objects.create(answer=answer, img_url=url)
        return answer

    # 답변 수정 (이미지교체)
    def update(self, instance: Answers, validated_data: Dict[str, Any]) -> Answers:
        # 새로 들어온 이미지 url리스트 확인
        image_urls: Optional[List[str]] = validated_data.pop("uploaded_images", None)
        # ⭐️새 이미지 들어오면 원래있던거 삭제하고 갈아끼움
        if image_urls is not None:
            instance.images.all().delete()
            for url in image_urls:
                AnswerImages.objects.create(answer=instance, img_url=url)
        # 나머지 필드 업데이트
        return super().update(instance, validated_data)
