from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers.presigned_url_serializer import PresignedUrlRequestSerializer
from apps.core.views.presigned_url import BasePresignedUrlView


class ProfilePresignedUrlView(BasePresignedUrlView):
    folder = "profiles"

    @extend_schema(
        summary="프로필 이미지 업로드용 Presigned URL 발급",
        tags=["Accounts"],
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(description="Presigned URL 발급 성공"),
            400: OpenApiResponse(description="지원하지 않는 파일 형식입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().put(request, *args, **kwargs)
