from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.permissions import IsStaffUser
from apps.subject.core.error_base import SubjectBaseAPIView
from apps.subject.serializers.course_serializers import (
    CourseCreateRequestSerializer,
    CourseCreateResponseSerializer,
    CourseDeleteResponseSerializer,
    CourseUpdateRequestSerializer,
    CourseUpdateResponseSerializer,
)
from apps.subject.services.course_admin_services import CourseAdminService


class CourseAdminCreateAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        tags=["Admin_students"],
        summary="어드민 과정 등록",
        description="새로운 과정을 등록합니다.",
        request=CourseCreateRequestSerializer,
        responses={
            201: CourseCreateResponseSerializer,
            400: OpenApiResponse(description="유효하지 않은 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CourseCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = CourseAdminService.create_course(serializer.validated_data)
        return Response(
            {"detail": "과정이 등록되었습니다.", "id": course.id},
            status=status.HTTP_201_CREATED,
        )


class CourseAdminUpdateDeleteAPIView(SubjectBaseAPIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        tags=["Admin_students"],
        summary="어드민 과정 정보 수정",
        description="과정 정보를 수정합니다.",
        request=CourseUpdateRequestSerializer,
        responses={
            200: CourseUpdateResponseSerializer,
            400: OpenApiResponse(description="feild_name : [이 필드는 필수 항목입니다.]"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="과정을 찾을 수 없습니다."),
        },
    )
    def patch(self, request: Request, course_id: int) -> Response:
        serializer = CourseUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        course = CourseAdminService.update_course(course_id, serializer.validated_data)
        return Response(CourseUpdateResponseSerializer(course).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Admin_students"],
        summary="어드민 과정 삭제",
        description="과정을 삭제합니다.",
        responses={
            200: CourseDeleteResponseSerializer,
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="과정을 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, course_id: int) -> Response:
        result = CourseAdminService.delete_course(course_id)
        return Response(result, status=status.HTTP_200_OK)
