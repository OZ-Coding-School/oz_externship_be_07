from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStaffUser
from apps.subject.core.error_responses import ErrorResponseSerializer
from apps.subject.serializers.subject_serializers import (
    SubjectCreateRequestSerializer,
    SubjectCreateResponseSerializer,
    SubjectListItemSerializer,
    SubjectScatterPointSerializer,
)
from apps.subject.services.subject_services import SubjectService


class SubjectListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        tags=["subjects"],
        summary="어드민 과목 생성 API",
        parameters=[
            OpenApiParameter(
                name="course_id",
                description="과정 ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
        ],
        request=SubjectCreateRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=SubjectCreateResponseSerializer,
                description="Created",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict",
            ),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "course_id": 1,
                    "title": "HTML",
                    "number_of_days": 5,
                    "number_of_hours": 40,
                    "thumbnail_img_url": "https://example.com/html.png",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "id": 1,
                    "course_id": 1,
                    "title": "HTML",
                    "number_of_days": 5,
                    "number_of_hours": 40,
                    "thumbnail_img_url": "https://example.com/html.png",
                    "status": "activated",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request: Request, course_id: int) -> Response:
        serializer = SubjectCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            subject = SubjectService.create_subject(
                course_id=course_id,
                data=serializer.validated_data,
            )
        except NotFound:
            return Response(
                {"error_detail": "해당 과정을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as exc:
            detail = str(exc.detail)

            if "동일한 이름의 과목이 이미 존재합니다." in detail:
                return Response(
                    {"error_detail": "동일한 이름의 과목이 이미 존재합니다."},
                    status=status.HTTP_409_CONFLICT,
                )

            if "유효하지 않은 과목 생성 요청입니다." in detail:
                return Response(
                    {"error_detail": "유효하지 않은 과목 생성 요청입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"error_detail": detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = SubjectCreateResponseSerializer(subject)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["subjects"],
        summary="어드민 과목 목록 API",
        parameters=[
            OpenApiParameter(
                name="course_id",
                description="과정 ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=SubjectListItemSerializer(many=True),
                description="OK",
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
            ),
        },
        examples=[
            OpenApiExample(
                "Response Example",
                value=[
                    {
                        "id": 1,
                        "course_id": 1,
                        "title": "test",
                        "status": "activated",
                        "thumbnail_img_url": "https://www.test.com",
                    }
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request: Request, course_id: int) -> Response:
        subjects = SubjectService.list_subjects_by_course(course_id=course_id)
        serializer = SubjectListItemSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubjectScatterAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    @extend_schema(
        tags=["subjects"],
        summary="어드민 과목별 학습시간/점수 산점도 조회",
        parameters=[
            OpenApiParameter(
                name="subject_id",
                description="과목 ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=SubjectScatterPointSerializer(many=True),
                description="OK",
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
            ),
        },
        examples=[
            OpenApiExample(
                "Response Example",
                value=[
                    {"time": 1.5, "score": 95},
                    {"time": 2.8, "score": 98},
                    {"time": 3.1, "score": 100},
                    {"time": 1.2, "score": 85},
                    {"time": 2.1, "score": 90},
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request: Request, subject_id: int) -> Response:
        try:
            submissions = SubjectService.get_subject_scatter_queryset(subject_id=subject_id)
        except NotFound:
            return Response(
                {"error_detail": "과목을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SubjectScatterPointSerializer(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
