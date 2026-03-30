from typing import Any

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_categoryserializers import (
    AdminCategorySerializer,
)
from apps.questions.services.admin.questions_admin_category_services import (
    AdminCategoryService,
)


class AdminCategoryCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="관리자 카테고리 등록",
        description="새로운 질문 카테고리를 등록합니다. 중복된 이름이나 존재하지 않는 부모 카테고리 설정 시 에러가 발생합니다.",
        request=AdminCategorySerializer,
        responses={
            201: AdminCategorySerializer,
            400: OpenApiResponse(
                description="잘못된 요청 (필수 값 누락 등)",
                examples=[
                    OpenApiExample(
                        "필수값 누락 예시",
                        value={"error_detail": "카테고리 종류와 이름은 필수 입력값입니다."},
                    )
                ],
            ),
            401: OpenApiResponse(
                description="인증 실패",
                examples=[
                    OpenApiExample(
                        "로그인 필요 예시",
                        value={"error_detail": "로그인이 필요합니다."},
                    )
                ],
            ),
            403: OpenApiResponse(
                description="권한 없음",
                examples=[
                    OpenApiExample(
                        "권한 부족 예시",
                        value={"error_detail": "카테고리 등록 권한이 없습니다."},
                    )
                ],
            ),
            404: OpenApiResponse(
                description="부모 카테고리 없음",
                examples=[
                    OpenApiExample(
                        "부모 카테고리 미존재 예시",
                        value={"error_detail": "부모 카테고리를 찾을 수 없습니다."},
                    )
                ],
            ),
            409: OpenApiResponse(
                description="중복된 이름",
                examples=[
                    OpenApiExample(
                        "이름 중복 예시",
                        value={"error_detail": "동일한 이름의 카테고리가 이미 존재합니다."},
                    )
                ],
            ),
        },
        tags=["Admin_qna"],
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AdminCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = AdminCategoryService.create_category(validated_data=serializer.validated_data)

        response_serializer = AdminCategorySerializer(category)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
