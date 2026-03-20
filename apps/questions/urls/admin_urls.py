from django.urls import path

from apps.questions.views.admin.admin_qna_categories_views import (
    AdminCategoryCreateAPIView,
)

# "questions" 중복 에러를 피하기 위해 이름을 고유하게 변경합니다.
app_name = "admin_questions"

urlpatterns = [
    # Admin_qna_category 등록 및 조회
    path(
        "admin/qna/categories/",
        AdminCategoryCreateAPIView.as_view(),
        name="admin_category_create",
    ),
]
