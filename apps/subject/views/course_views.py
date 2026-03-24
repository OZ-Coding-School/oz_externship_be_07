from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.subject.core.error_base import SubjectBaseAPIView
from apps.subject.serializers.cohort_serializers import ErrorDetailStringSerializer
from apps.subject.serializers.course_serializers import CourseListItemSerializer
from apps.subject.services.course_services import CourseService


@extend_schema(
    tags=["course"],
    summary="과정 리스트 조회 API",
    responses={
        200: CourseListItemSerializer(many=True),
        401: ErrorDetailStringSerializer,
        403: ErrorDetailStringSerializer,
    },
)
class CourseListAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        courses = CourseService.get_course_list()

        serializer = CourseListItemSerializer(courses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
