from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.community.views.comment_views import CommentViewSet

# 1. 라우터 생성
router = DefaultRouter()
# 2. ViewSet 등록 (주소창에 들어갈 이름 정하기)
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    # 3. 라우터의 URL 패턴을 포함시킴
    path("", include(router.urls)),
]
