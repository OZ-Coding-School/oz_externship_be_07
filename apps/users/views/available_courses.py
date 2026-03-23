from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subject.models.cohort_models import Cohort
from apps.users.serializers.available_courses import AvailableCourseSerializer


class AvailableCourseListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="수강 신청 가능한 기수 조회",
        responses={
            200: AvailableCourseSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        },
    )
    def get(self, request: Any) -> Response:
        available_cohorts = Cohort.objects.filter(status="PENDING").select_related("course")
        serializer = AvailableCourseSerializer(available_cohorts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            return Response(
                {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

        return super().handle_exception(exc)
