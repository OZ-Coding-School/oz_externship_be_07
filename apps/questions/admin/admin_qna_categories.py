from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.questions.models import QuestionCategories
from apps.questions.serializers.admin_qna_categoryserializers import AdminCategoryCreateSerializer

# 어드민 카테고리 등록 API 기능 구현
class AdminCategoryCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        # 필수 입력값 검증 (카테고리 종류, 이름)
        category_type = request.data.get('category_type')
        name = request.data.get('name')

        if not category_type or not name:
            return Response(
                {"error_detail": "카테고리 종류와 이름은 필수 입력값입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        parent_id = request.data.get('parent_id')
        if parent_id and not QuestionCategories.objects.filter(id=parent_id).exists():
            return Response(
                {"error_detail": "부모 카테고리를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 중복 체크 및 데이터 저장
        serializer = AdminCategoryCreateSerializer(data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                # 카테고리 생성 성공
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            if "이미 존재합니다" in str(e):
                return Response(
                    {"error_detail": "동일한 이름의 카테고리가 이미 존재합니다."},
                    status=status.HTTP_409_CONFLICT
                )

            return Response(
                {"error_detail": "유효하지 않은 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )