from django.db import IntegrityError
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStaffUser
from apps.subject.models.enrollment_request_models import EnrollmentRequest
from apps.users.serializers.admin.user_management import (
    AdminEnrollmentAcceptSerializer,
    AdminEnrollmentRejectSerializer,
    AdminUserEnrollmentSerializer,
    AdminUserRoleUpdateSerializer,
    StudentEnrollmentTrendRequestSerializer,
    StudentEnrollmentTrendResponseSerializer,
)
from apps.users.services.admin.user_enrollment_trend_analytics import (
    get_student_enrollment_trend_service,
)
from apps.users.services.admin.user_management import (
    accept_enrollment_requests,
    delete_user_by_admin,
    reject_enrollment_requests,
    update_user_role,
)


@extend_schema_view(
    list=extend_schema(summary="관리자용 수강생 등록 요청 목록 조회 API", tags=["Admin_accounts"]),
    retrieve=extend_schema(summary="관리자용 수강생 등록 요청 목록 상세조회 API", tags=["Admin_accounts"]),
)
class AdminUserEnrollmentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet[EnrollmentRequest]
):
    """
    권한: 운영진(TA, OM, LC, ADMIN) 전용 API
    """

    queryset = EnrollmentRequest.objects.select_related("user", "cohort", "cohort__course").all()
    serializer_class = AdminUserEnrollmentSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # 필터/검색 필드 설정
    filterset_fields = ["status"]
    search_fields = ["user__name", "user__email"]
    ordering = ["-created_at"]


class AdminEnrollmentAcceptAPIView(APIView):
    """
    관리자 권한을 가진 유저는 수강 등록 신청을 승인할 수 있습니다.

    조회된 목록들에서 승인할 신청 내역들을 선택한 후 페이지 내에 위치한 선택 항목 승인 버튼을 클릭하여 일괄 승인할 수 있습니다.
    """

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="관리자용 수강생 등록 요청 승인 API",
        tags=["Admin_accounts"],
        request=AdminEnrollmentAcceptSerializer,
        responses={
            200: {"description": "OK", "example": {"detail": "수강생 등록 신청들에 대한 승인 요청이 처리되었습니다."}},
            400: OpenApiResponse(description="이 필드는 필수 항목입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = AdminEnrollmentAcceptSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # 서비스 함수 호출
        updated_count = accept_enrollment_requests(serializer.validated_data["enrollments"])

        if updated_count == 0:
            return Response(
                {"error_detail": "승인 가능한 대기 상태의 신청 건이 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"detail": f"{updated_count}건의 수강 신청이 승인되었습니다."}, status=status.HTTP_200_OK)


class AdminEnrollmentRejectAPIView(APIView):
    """
    관리자 권한을 가진 유저는 수강 등록 신청을 반려할 수 있습니다.

    조회된 목록들에서 반려할 신청 내역들을 선택한 후 페이지 내에 위치한 선택 항목 반려 버튼을 클릭하여 일괄 반려할 수 있습니다.
    """

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="관리자용 수강생 등록 요청 반려 API",
        tags=["Admin_accounts"],
        request=AdminEnrollmentRejectSerializer,
        responses={
            200: {"description": "OK", "example": {"detail": "수강생 등록 신청들에 대한 반려 요청이 처리되었습니다."}},
            400: OpenApiResponse(description="이 필드는 필수 항목입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = AdminEnrollmentRejectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # 서비스 함수 호출
        updated_count = reject_enrollment_requests(serializer.validated_data["enrollments"])

        if updated_count == 0:
            return Response(
                {"error_detail": "반려 가능한 대기 상태의 신청 건이 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"detail": f"{updated_count}건의 수강 신청이 반려되었습니다."}, status=status.HTTP_200_OK)


class AdminUserRoleUpdateAPIView(APIView):
    """
    관리자 페이지에서 사용자의 권한을 변경합니다.
    """

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="어드민 페이지 권한 변경 API",
        tags=["Admin_accounts"],
        request=AdminUserRoleUpdateSerializer,
        responses={
            200: OpenApiResponse(description="권한이 변경되었습니다."),
            400: OpenApiResponse(description="조교 권한으로 변경 시 필수 필드입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
        },
    )
    def patch(self, request: Request, account_id: int) -> Response:
        serializer = AdminUserRoleUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            update_user_role(user_id=account_id, role_data=serializer.validated_data)
        except IntegrityError:
            return Response(
                {"error_detail": "존재하지 않는 기수(cohort) 또는 코스(course) 정보입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "권한이 변경되었습니다."}, status=status.HTTP_200_OK)


class AdminStudentEnrollmentTrendAPIView(APIView):

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="어드민 페이지 수강 등록 추세 분석 API",
        tags=["Admin_accounts"],
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


class AdminUserDeleteAPIView(APIView):
    """
    관리자 페이지에서 사용자를 삭제하는 API입니다.
    """

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="어드민 페이지 사용자 삭제 API",
        tags=["Admin_accounts"],
        responses={
            200: OpenApiResponse(description="유저 데이터가 삭제되었습니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, account_id: int) -> Response:
        try:
            deleted_pk = delete_user_by_admin(account_id=account_id)
            return Response({"detail": f"유저 데이터가 삭제되었습니다. - pk: {deleted_pk}"}, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error_detail": "사용자 정보를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

        if isinstance(exc, PermissionDenied):
            return Response({"error_detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        return super().handle_exception(exc)
