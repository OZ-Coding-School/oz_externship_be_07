from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from apps.exam.services.exam_crud_services import ExamService
from apps.exam.serializers.exam_serializers import (
    ExamCreateUpdateSerializer,
    ExamListSerializer,
    ExamDetailSerializer
)


class ExamPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    page_query_param = "page"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'size': self.get_page_size(self.request),
            'total_count': self.page.paginator.count,
            'exams': data
        })


class ExamListCreateAPIView(APIView):
    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 목록 조회",
        description="검색 키워드, 과목 ID, 정렬 조건을 받아 페이지네이션된 시험 목록을 반환합니다.",
        parameters=[
            OpenApiParameter(name='page', description='페이지 번호', type=int),
            OpenApiParameter(name='size', description='페이지당 아이템 개수', type=int),
            OpenApiParameter(name='search_keyword', description='시험 제목 검색어', type=str),
            OpenApiParameter(name='subject_id', description='과목 ID 필터', type=int),
            OpenApiParameter(name='sort', description='정렬 필드 (id, title, created_at 등)', type=str),
            OpenApiParameter(name='order', description='정렬 순서 (asc, desc)', type=str),
        ],
        responses={
            200: ExamListSerializer(many=True),
            400: OpenApiResponse(description="유효하지 않은 조회 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="쪽지시험 목록 조회 권한이 없습니다."),
        }
    )
    def get(self, request):
        queryset = ExamService.get_exam_queryset(request.query_params)
        paginator = ExamPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ExamListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ExamListSerializer(queryset, many=True)
        return Response({'exams': serializer.data})

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 생성",
        description="새로운 쪽지시험을 생성합니다.",
        request=ExamCreateUpdateSerializer,
        responses={
            201: ExamCreateUpdateSerializer,
            400: "유효하지 않은 시험 생성 요청입니다.",
            401: "자격 인증 데이터가 제공되지 않았습니다.",
            403: "쪽지시험 생성 권한이 없습니다.",
            404: "해당 과목 정보를 찾을 수 없습니다.",
            409: "동일한 이름의 시험이 이미 존재합니다."
        }
    )
    def post(self, request):
        serializer = ExamCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            exam = ExamService.create_exam(serializer.validated_data)
            # 응답 형식: {id, title, subject_id, thumbnail_img_url}
            return Response(ExamCreateUpdateSerializer(exam).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamDetailAPIView(APIView):
    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 상세 조회",
        description="시험의 상세 정보와 포함된 질문 리스트를 조회합니다.",
        responses={200: ExamDetailSerializer}
    )
    def get(self, request, exam_id):
        exam = ExamService.get_exam_detail(exam_id)
        serializer = ExamDetailSerializer(exam)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 수정",
        description="기존 쪽지시험 정보를 수정합니다.",
        request=ExamCreateUpdateSerializer,
        responses={
            200: ExamCreateUpdateSerializer,
            400: "유효하지 않은 시험 생성 요청입니다.",
            401: "자격 인증 데이터가 제공되지 않았습니다.",
            403: "쪽지시험 생성 권한이 없습니다.",
            404: "해당 과목 정보를 찾을 수 없습니다.",
            409: "동일한 이름의 시험이 이미 존재합니다."
        }
    )
    def put(self, request, exam_id):
        serializer = ExamCreateUpdateSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            exam = ExamService.update_exam(exam_id, serializer.validated_data)
            return Response(ExamCreateUpdateSerializer(exam).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 삭제",
        description="특정 쪽지시험을 삭제합니다.",
        responses={
            201: "id",
            400: "유효하지 않은 시험 생성 요청입니다.",
            401: "자격 인증 데이터가 제공되지 않았습니다.",
            403: "쪽지시험 삭제 권한이 없습니다.",
            404: "삭제하려는 쪽지시험 정보를 찾을 수 없습니다.",
            409: "쪽지시험 삭제 중 충돌이 발생했습니다."

        }
    )
    def delete(self, request, exam_id):
        """DELETE: 삭제"""
        ExamService.delete_exam(exam_id)
        return Response({"id": exam_id }, status=status.HTTP_201_CREATED)