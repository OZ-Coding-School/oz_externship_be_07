from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.serializers.admin.admin_qna_questions_list_serializers import (
    AdminQuestionDetailSerializer,
)
from apps.questions.services.admin.admin_qna_questions_list_services import (
    AdminQuestionDetailService,
)


class AdminQuestionDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="관리자 질의응답 상세 조회",
        description="특정 질의응답의 상세 내용과 작성자 정보, 그리고 등록된 답변 및 댓글 목록을 조회합니다.",
        responses={
            200: AdminQuestionDetailSerializer,
            400: OpenApiResponse(
                description="잘못된 요청",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 요청 예시",
                        value={"error_detail": "유효하지 않은 질문 상세 조회 요청입니다."},
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
                        value={"error_detail": "질의응답 상세 조회 권한이 없습니다."},
                    )
                ],
            ),
            404: OpenApiResponse(
                description="질문 미존재",
                examples=[
                    OpenApiExample(
                        "대상 미존재 예시",
                        value={"error_detail": "해당 질문을 찾을 수 없습니다."},
                    )
                ],
            ),
        },
        tags=["Admin_qna"],
    )
    def get(self, request: Request, question_id: int) -> Response:
        question = AdminQuestionDetailService.get_question_detail(question_id)

        serializer = AdminQuestionDetailSerializer(question)

        return Response(serializer.data, status=status.HTTP_200_OK)
