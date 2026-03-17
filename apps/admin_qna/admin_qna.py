from apps.questions.serializers.questions_serializers import AdminQuestionListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from apps.questions.models import Questions


# 어드민 질의응답 목록 조회 API
class AdminQuestionListAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 20))
            search_keyword = request.query_params.get('search_keyword')
            category_id = request.query_params.get('category_id')
            answer_status = request.query_params.get('answer_status')
            sort = request.query_params.get('sort', 'latest')

            #최신순 정렬 대응
            queryset = Questions.objects.all()

            # 필터링 : 검색어
            if search_keyword:
                queryset = queryset.filter(
                    Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword)
                )

            # 필터링 : 카테고리 ID
            if category_id:
                queryset = queryset.filter(category_id=category_id)

            # 필터링: 답변 여부 (Y/N)
            if answer_status:
                queryset = queryset.filter(has_answer=(answer_status == 'Y'))

            # 정렬
            if sort == 'latest':
                queryset = queryset.order_by('-created_at')
            else:
                queryset = queryset.order_by('created_at')

            # 페이지네이션 계산
            total_count = queryset.count()
            start = (page - 1) * size
            end = start + size

            serializer = AdminQuestionListSerializer(queryset[start:end], many=True)

            # 명세서 Response Body 규격 반영
            return Response({
                "page": page,
                "size": size,
                "total_count": total_count,
                "questions": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"error_detail": "유효하지 않은 목록 조회 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
