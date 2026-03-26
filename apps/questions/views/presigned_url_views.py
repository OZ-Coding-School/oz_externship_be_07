from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers.presigned_url_serializer import PresignedUrlRequestSerializer
from apps.core.views.presigned_url import BasePresignedUrlView


class AnswerPresignedUrlView(BasePresignedUrlView):
    folder = "answers"

    # 답변 이미지 Presigned URL 발급
    @extend_schema(
        tags=["Answers"],
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(description="Presigned URL 발급 성공"),
            400: OpenApiResponse(description="지원하지 않는 파일 형식입니다."),
            401: OpenApiResponse(description="로그인한 사용자만 요청할 수 있습니다."),
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().put(request, *args, **kwargs)


class QuestionPresignedUrlView(BasePresignedUrlView):
    folder = "questions"

    # 질문 이미지 Presigned URL 발급
    @extend_schema(
        tags=["qna"],
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(description="Presigned URL 발급 성공"),
            400: OpenApiResponse(description="지원하지 않는 파일 형식입니다."),
            401: OpenApiResponse(description="로그인한 사용자만 요청할 수 있습니다."),
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().put(request, *args, **kwargs)
