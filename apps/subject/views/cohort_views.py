from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.subject.serializers.cohort_serializers import (
    CohortListItemSerializer,
    ErrorDetailStringSerializer,
)
from apps.subject.services.cohort_services import CohortService
from apps.subject.core.error_base import SubjectBaseAPIView
from apps.subject.views.cohort_permissions import CanViewCohortList

ALLOWED_ADMIN_ROLES = {"TA", "LC", "OM", "ADMIN"}


def error_response(*, message: str, http_status: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response({"error_detail": message}, status=http_status)


def check_authenticated(request: Request) -> Response | None:
    if not request.user or not request.user.is_authenticated:
        return error_response(
            message="자격 인증 데이터가 제공되지 않았습니다.",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )
    return None


def check_admin_role(request: Request) -> Response | None:
    auth_error = check_authenticated(request)
    if auth_error:
        return auth_error

    role = str(getattr(request.user, "role", "")).upper()
    if role not in ALLOWED_ADMIN_ROLES:
        return error_response(
            message="권한이 없습니다.",
            http_status=status.HTTP_403_FORBIDDEN,
        )
    return None


class CohortListAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated, CanViewCohortList]

    @extend_schema(
        tags=["subjects"],
        summary="기수 리스트 조회 API",
        responses={
            200: OpenApiResponse(response=CohortListItemSerializer(many=True), description="OK"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
        },
    )
    def get(self, request: Request, course_id: int) -> Response:

        cohorts = CohortService.get_cohorts_by_course_id(course_id=course_id)

        data = [
            {
                "id": cohort.id,
                "course_id": cohort.course_id,
                "number": cohort.number,
                "status": cohort.status,
            }
            for cohort in cohorts
        ]
        return Response(data, status=status.HTTP_200_OK)
