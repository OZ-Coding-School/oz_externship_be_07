from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Exam
from .serializers import (
    ExamCreateSerializer, ExamListSerializer,
    ExamDetailSerializer, ExamUpdateSerializer,
    ExamDeleteRequestSerializer
)
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response


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
        serializer = ExamCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamDetailAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ExamDetailSerializer

    @extend_schema(
        summary="쪽지시험 상세 조회",
        description="특정 ID의 쪽지시험 상세 정보와 질문 목록을 조회합니다.",
        responses={200: ExamDetailSerializer},
        tags=['쪽지시험 관리']
    )
    def get(self, request, exam_id):
        exam = self.get_object(exam_id)
        serializer = ExamDetailSerializer(exam)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="쪽지시험 수정",
        description="기존 쪽지시험의 정보를 수정합니다. 이미지 변경이 없을 경우 필드를 비워둘 수 있습니다.",
        request=ExamUpdateSerializer,
        responses={200: ExamUpdateSerializer},
        tags=['쪽지시험 관리']
    )
    def put(self, request, exam_id):
        exam = self.get_object(exam_id)
        serializer = ExamUpdateSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="쪽지시험 삭제",
        description="특정 쪽지시험을 삭제합니다. 성공 시 삭제된 시험의 ID를 반환합니다.",
        responses={201: ExamDeleteRequestSerializer},
        tags=['쪽지시험 관리']
    )
    def delete(self, request, exam_id):
        exam = self.get_object(exam_id)
        exam.delete()
        return Response({"id": exam_id}, status=status.HTTP_200_OK)

