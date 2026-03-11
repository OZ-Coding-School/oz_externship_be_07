from django.shortcuts import render
from django.http import Http404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Exam
from .serializers import (
    ExamCreateSerializer, ExamListSerializer,
    ExamDetailSerializer, ExamUpdateSerializer,
    ExamDeleteRequestSerializer
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
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
class ExamListCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="쪽지시험 목록 조회",
        description="관리자용 쪽지시험 목록을 조회합니다. 과목 필터 및 키워드 검색이 가능합니다.",
        responses={200: ExamListSerializer(many=True)},
        tags=['쪽지시험 관리']
    )
    def get(self, request):
        # 검색/필터링 로직 (정의서 요구사항 반영)
        subject_id = request.query_params.get('subject_id')
        search_keyword = request.query_params.get('search_keyword')

        exams = Exam.objects.all().order_by('-created_at')

        if subject_id:
            exams = exams.filter(subject_id=subject_id)
        if search_keyword:
            exams = exams.filter(title__icontains=search_keyword)

        serializer = ExamListSerializer(exams, many=True)
        # 요구사항 정의서 Success Response Example 구조 반영
        return Response({
            "page": 1,
            "size": 10,
            "total_count": exams.count(),
            "exams": serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="쪽지시험 생성",
        description="새로운 쪽지시험을 생성합니다. 썸네일 이미지는 binary 파일로 전송해야 합니다.",
        request=ExamCreateSerializer,
        responses={201: ExamCreateSerializer},
        tags=['쪽지시험 관리']
    )
    def post(self, request):



    @extend_schema(
    )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
    )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
            )

