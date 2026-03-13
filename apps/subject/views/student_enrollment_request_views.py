from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subject.serializers.student_enrollment_request_serializers import (
    StudentEnrollmentAcceptErrorResponseSerializer,
    StudentEnrollmentAcceptRequestSerializer,
    StudentEnrollmentAcceptResponseSerializer,
)
from apps.subject.services.student_enrollment_request_services import (
    StudentEnrollmentRequestService,
)


class IsAdminUserLike:
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class AdminStudentEnrollmentAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserLike]

    @extend_schema(
        tags=["subjects"],
        summary="어드민 수강생 등록 요청 승인 API",
        request=StudentEnrollmentAcceptRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=StudentEnrollmentAcceptResponseSerializer,
                description="승인 성공",
            ),
            400: OpenApiResponse(
                response=StudentEnrollmentAcceptErrorResponseSerializer,
                description="잘못된 요청",
            ),
            401: OpenApiResponse(
                response=StudentEnrollmentAcceptErrorResponseSerializer,
                description="인증 실패",
            ),
            403: OpenApiResponse(
                response=StudentEnrollmentAcceptErrorResponseSerializer,
                description="권한 없음",
            ),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "enrollments": [1, 2, 3, 4]
                },
                request_only=True,
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "detail": "수강생 등록 신청들에 대한 승인 요청이 처리되었습니다."
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad Request Example",
                value={
                    "error_detail": {
                        "enrollments": [
                            "이 필드는 필수 항목입니다."
                        ]
                    }
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        serializer = StudentEnrollmentAcceptRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            StudentEnrollmentRequestService.accept_enrollments(
                enrollment_ids=serializer.validated_data["enrollments"]
            )
        except Exception as exc:
            detail = getattr(exc, "detail", None)

            if detail:
                return Response(
                    {"error_detail": detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"error_detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "수강생 등록 신청들에 대한 승인 요청이 처리되었습니다."
            },
            status=status.HTTP_200_OK,
        )