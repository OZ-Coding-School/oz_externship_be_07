from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin.user_enrollment_reject import (
    AdminEnrollmentRejectSerializer,
)
from apps.users.services.admin.user_enrollment_action import reject_enrollment_requests
from apps.users.views.admin.user_enrollment import IsStaffUser


class AdminEnrollmentRejectAPIView(APIView):
    """
    관리자 권한을 가진 유저는 수강 등록 신청을 반려할 수 있습니다.

    조회된 목록들에서 반려할 신청 내역들을 선택한 후 페이지 내에 위치한 선택 항목 반려 버튼을 클릭하여 일괄 반려할 수 있습니다.
    """

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="관리자용 수강생 등록 요청 반려 API",
        tags=["admin_accounts"],
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
