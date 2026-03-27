from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStaffUser
from apps.users.serializers.admin.user_enrollment_trend_analytics import (
    StudentEnrollmentTrendRequestSerializer,
    StudentEnrollmentTrendResponseSerializer,
)
from apps.users.services.admin.user_enrollment_trend_analytics import (
    get_student_enrollment_trend_service,
)


class AdminStudentEnrollmentTrendAPIView(APIView):

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="어드민 페이지 수강 등록 추세 분석 API",
        tags=["admin_accounts"],
        parameters=[StudentEnrollmentTrendRequestSerializer],
        responses={
            200: StudentEnrollmentTrendResponseSerializer,
            400: OpenApiResponse(description="interval 값이 올바르지 않습니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        request_serializer = StudentEnrollmentTrendRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        interval = request_serializer.validated_data["interval"]

        data = get_student_enrollment_trend_service(interval)

        response_serializer = StudentEnrollmentTrendResponseSerializer(data=data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.validated_data)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if isinstance(exc, PermissionDenied):
            return Response(
                {"error_detail": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)
