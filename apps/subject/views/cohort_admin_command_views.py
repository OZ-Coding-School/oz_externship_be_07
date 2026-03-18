from typing import Any

from django.db import IntegrityError
from django.http import Http404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subject.serializers.cohort_serializers import (
    CohortCreateRequestSerializer,
    CohortCreateResponseSerializer,
    CohortUpdateRequestSerializer,
    CohortUpdateResponseSerializer,
    ErrorDetailFieldSerializer,
    ErrorDetailStringSerializer,
)
from apps.subject.services.cohort_services import CohortService
from apps.subject.views.cohort_views import check_admin_role, error_response


def field_error_response(*, errors: dict[str, Any], http_status: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response({"error_detail": errors}, status=http_status)


class AdminCohortCreateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["subjects"],
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
                value={"detail": "기수가 등록되었습니다.", "id": 1},
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        permission_error = check_admin_role(request)
        if permission_error:
            return permission_error

        serializer = CohortCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return field_error_response(errors=dict(serializer.errors))

        try:
            cohort = CohortService.create_cohort(validated_data=serializer.validated_data)
        except IntegrityError:
            return field_error_response(
                errors={"number": ["이미 해당 과정에 동일한 기수가 존재합니다."]},
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = CohortCreateResponseSerializer({"detail": "기수가 등록되었습니다.", "id": cohort.id})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AdminCohortUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["subjects"],
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
    def patch(self, request: Request, cohort_id: int) -> Response:
        permission_error = check_admin_role(request)
        if permission_error:
            return permission_error

        from apps.subject.models.cohort_models import Cohort

        try:
            cohort = Cohort.objects.get(pk=cohort_id)
        except Cohort.DoesNotExist:
            return error_response(
                message="기수를 찾을 수 없습니다.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CohortUpdateRequestSerializer(instance=cohort, data=request.data, partial=True)
        if not serializer.is_valid():
            return field_error_response(errors=dict(serializer.errors))

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
        except IntegrityError:
            return field_error_response(
                errors={"number": ["이미 해당 과정에 동일한 기수가 존재합니다."]},
                http_status=status.HTTP_400_BAD_REQUEST,
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
