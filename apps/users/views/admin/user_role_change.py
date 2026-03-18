from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin.user_role_update import AdminUserRoleUpdateSerializer
from apps.users.services.admin.user_role_update import update_user_role
from apps.users.views.admin.user_enrollment import IsStaffUser


class AdminUserRoleUpdateAPIView(APIView):
    """
    관리자 페이지에서 사용자의 권한을 변경합니다.
    """

    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        summary="어드민 페이지 권한 변경 API",
        tags=["admin_accounts"],
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

        update_user_role(user_id=account_id, role_data=serializer.validated_data)

        return Response({"detail": "권한이 변경되었습니다."}, status=status.HTTP_200_OK)
