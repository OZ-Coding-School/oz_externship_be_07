from typing import cast

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.models import User
from apps.users.serializers.mycourse_check_serializers import (
    MyEnrolledCourseSerializer,
)


class MyEnrolledCourseView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="내 수강 목록 조회",
        tags=["Accounts"],
        responses={
            200: MyEnrolledCourseSerializer(many=True),
            401: OpenApiExample("인증 에러", value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."}),
        },
    )
    def get(self, request: Request) -> Response:
        user = cast(User, request.user)
        enrollments = user.enrollmentrequest_set.all().select_related("cohort", "cohort__course")

        data = [{"cohort": en.cohort, "course": en.cohort.course} for en in enrollments]

        serializer = MyEnrolledCourseSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
