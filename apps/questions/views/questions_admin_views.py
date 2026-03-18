from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.models import QuestionCategories


class AdminCategoryCreateAPIView(APIView):
    def post(self, request: Request) -> Response:
        try:
            name = request.data.get("name")
            parent_id = request.data.get("parent")

            # 1. 필수값 체크
            if not name:
                return Response({"error": "이름은 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 2. 부모 카테고리 체크
            parent = None
            if parent_id:
                parent = QuestionCategories.objects.filter(id=parent_id).first()
                if not parent:
                    return Response({"error": "존재하지 않는 부모 카테고리입니다."}, status=status.HTTP_404_NOT_FOUND)

            # 3. 생성
            category = QuestionCategories.objects.create(name=name, parent=parent)

            return Response(
                {"id": category.id, "name": category.name, "parent": category.parent.id if category.parent else None},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            # 예기치 못한 진짜 서버 에러만 500으로 처리
            return Response({"error_detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
