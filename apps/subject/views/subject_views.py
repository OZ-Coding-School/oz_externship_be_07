from django.http import Http404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subject.serializers.subject_serializers import (
    ErrorResponseSerializer,
    SubjectCreateRequestSerializer,
    SubjectCreateResponseSerializer,
    SubjectDetailResponseSerializer,
    SubjectListItemSerializer,
    SubjectScatterPointSerializer,
    SubjectUpdateRequestSerializer,
)
from apps.subject.services.subject_services import SubjectService


class IsAdminUserLike:
    """
    프로젝트에 맞는 실제 권한 클래스로 교체하세요.
    예:
    - DRF IsAdminUser
    - 커스텀 관리자 권한
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class AdminSubjectCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserLike]

    @extend_schema(
        tags=["subjects"],
        summary="어드민 과목 생성 API",
        request=SubjectCreateRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=SubjectCreateResponseSerializer,
                description="과목 생성 성공",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="유효하지 않은 요청",
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="인증 실패",
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="권한 없음",
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="과정을 찾을 수 없음",
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="중복 과목명",
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
                    "status": "ACTIVATED",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request):
        serializer = SubjectCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            subject = SubjectService.create_subject(data=serializer.validated_data)
        except Http404:
            return Response(
                {"error_detail": "해당 과정을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:
            detail = str(exc)

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


class AdminSubjectListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserLike]

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
                description="과목 목록 조회 성공",
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="인증 실패",
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="권한 없음",
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
                        "status": "ACTIVATED",
                        "thumbnail_img_url": "https://www.test.com",
                    }
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request, course_id: int):
        subjects = SubjectService.list_subjects_by_course(course_id=course_id)
        serializer = SubjectListItemSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminSubjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserLike]

    @extend_schema(
        tags=["subjects"],
        summary="어드민 과목 상세 조회 API",
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
            200: SubjectDetailResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, subject_id: int):
        try:
            subject = SubjectService.get_subject(subject_id=subject_id)
        except Http404:
            return Response(
                {"error_detail": "과목을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SubjectDetailResponseSerializer(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["subjects"],
        summary="어드민 과목 수정 API",
        request=SubjectUpdateRequestSerializer,
        responses={
            200: SubjectDetailResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            409: ErrorResponseSerializer,
        },
    )
    def patch(self, request, subject_id: int):
        serializer = SubjectUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            subject = SubjectService.update_subject(
                subject_id=subject_id,
                data=serializer.validated_data,
            )
        except Http404:
            return Response(
                {"error_detail": "과목을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:
            detail = str(exc)

            if "동일한 이름의 과목이 이미 존재합니다." in detail:
                return Response(
                    {"error_detail": "동일한 이름의 과목이 이미 존재합니다."},
                    status=status.HTTP_409_CONFLICT,
                )

            return Response(
                {"error_detail": detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = SubjectDetailResponseSerializer(subject)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["subjects"],
        summary="어드민 과목 삭제 API",
        responses={
            204: OpenApiResponse(description="과목 삭제 성공"),
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, subject_id: int):
        try:
            SubjectService.delete_subject(subject_id=subject_id)
        except Http404:
            return Response(
                {"error_detail": "과목을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminSubjectScatterAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserLike]

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
                description="산점도 조회 성공",
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="인증 실패",
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="권한 없음",
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="과목을 찾을 수 없음",
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
    def get(self, request, subject_id: int):
        try:
            submissions = SubjectService.get_subject_scatter_queryset(subject_id=subject_id)
        except Http404:
            return Response(
                {"error_detail": "과목을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SubjectScatterPointSerializer(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
