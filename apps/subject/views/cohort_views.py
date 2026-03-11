from django.db import IntegrityError
from django.http import Http404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subject.serializers.cohort_serializers import (
    CohortCreateRequestSerializer,
    CohortCreateResponseSerializer,
    CohortListItemSerializer,
    CohortStudentItemSerializer,
    CohortUpdateRequestSerializer,
    CohortUpdateResponseSerializer,
    ErrorDetailFieldSerializer,
    ErrorDetailStringSerializer,
)
from apps.subject.services.cohort_services import CohortService

ALLOWED_ADMIN_ROLES = {"TA", "LC", "OM", "ADMIN"}


def error_response(*, message, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"error_detail": message}, status=http_status)


def field_error_response(*, errors, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"error_detail": errors}, status=http_status)


def check_authenticated(request):
    if not request.user or not request.user.is_authenticated:
        return error_response(
            message="자격 인증 데이터가 제공되지 않았습니다.",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )
    return None


def check_admin_role(request):
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


class AdminCohortCreateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["쪽지시험 기수 관리"],
        summary="어드민 페이지 기수 등록 API",
        request=CohortCreateRequestSerializer,
        responses={
            201: OpenApiResponse(response=CohortCreateResponseSerializer, description="Created"),
            400: OpenApiResponse(response=ErrorDetailFieldSerializer, description="Bad Request"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
        },
        examples=[
            OpenApiExample(
                "request example",
                value={
                    "course_id": 1,
                    "number": 15,
                    "max_student": 30,
                    "start_date": "2025-11-01",
                    "end_date": "2026-04-30",
                    "status": "PREPARING",
                },
                request_only=True,
            ),
            OpenApiExample(
                "success example",
                value={
                    "detail": "기수가 등록되었습니다.",
                    "id": 1,
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request):
        permission_error = check_admin_role(request)
        if permission_error:
            return permission_error

        serializer = CohortCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return field_error_response(errors=serializer.errors)

        try:
            cohort = CohortService.create_cohort(validated_data=serializer.validated_data)
        except Http404:
            return field_error_response(
                errors={"course_id": ["해당 과정을 찾을 수 없습니다."]},
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError:
            return field_error_response(
                errors={"number": ["이미 해당 과정에 동일한 기수가 존재합니다."]},
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = CohortCreateResponseSerializer(
            {
                "detail": "기수가 등록되었습니다.",
                "id": cohort.id,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CohortListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["쪽지시험 기수 관리"],
        summary="기수 리스트 조회 API",
        responses={
            200: OpenApiResponse(response=CohortListItemSerializer(many=True), description="OK"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
        },
    )
    def get(self, request, course_id: int):
        auth_error = check_authenticated(request)
        if auth_error:
            return auth_error

        role = str(getattr(request.user, "role", "")).upper()
        if role not in ALLOWED_ADMIN_ROLES:
            return error_response(
                message="이 리소스를 조회할 권한이 없습니다.",
                http_status=status.HTTP_403_FORBIDDEN,
            )

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
        return Response(CohortListItemSerializer(data, many=True).data, status=status.HTTP_200_OK)


class AdminCohortUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["쪽지시험 기수 관리"],
        summary="어드민 페이지 기수 정보 수정 API",
        request=CohortUpdateRequestSerializer,
        responses={
            200: OpenApiResponse(response=CohortUpdateResponseSerializer, description="OK"),
            400: OpenApiResponse(response=ErrorDetailFieldSerializer, description="Bad Request"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
            404: OpenApiResponse(response=ErrorDetailStringSerializer, description="Not Found"),
        },
    )
    def patch(self, request, cohort_id: int):
        permission_error = check_admin_role(request)
        if permission_error:
            return permission_error

        try:
            from apps.subject.models.cohort_models import Cohort

            cohort = Cohort.objects.get(pk=cohort_id)
        except Cohort.DoesNotExist:
            return error_response(
                message="기수를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CohortUpdateRequestSerializer(instance=cohort, data=request.data, partial=True)
        if not serializer.is_valid():
            return field_error_response(errors=serializer.errors)

        try:
            updated_cohort = CohortService.update_cohort(
                cohort_id=cohort_id,
                validated_data=serializer.validated_data,
            )
        except Http404:
            return error_response(
                message="기수를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = CohortUpdateResponseSerializer(
            {
                "id": updated_cohort.id,
                "course_id": updated_cohort.course_id,
                "number": updated_cohort.number,
                "max_student": updated_cohort.max_student,
                "start_date": updated_cohort.start_date,
                "end_date": updated_cohort.end_date,
                "status": updated_cohort.status,
                "updated_at": updated_cohort.updated_at,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class AdminCohortStudentListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["쪽지시험 기수 관리"],
        summary="어드민 기수별 수강생 목록 조회 API",
        responses={
            200: OpenApiResponse(response=CohortStudentItemSerializer(many=True), description="OK"),
            401: OpenApiResponse(response=ErrorDetailStringSerializer, description="Unauthorized"),
            403: OpenApiResponse(response=ErrorDetailStringSerializer, description="Forbidden"),
            404: OpenApiResponse(response=ErrorDetailStringSerializer, description="Not Found"),
        },
    )
    def get(self, request, cohort_id: int):
        permission_error = check_admin_role(request)
        if permission_error:
            return permission_error

        try:
            cohort_students = CohortService.get_cohort_students(cohort_id=cohort_id)
        except Http404:
            return error_response(
                message="기수를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        data = [
            {
                "value": cohort_student.user.nickname,
                "label": cohort_student.user.name,
            }
            for cohort_student in cohort_students
        ]
        return Response(CohortStudentItemSerializer(data, many=True).data, status=status.HTTP_200_OK)
