from django.urls import path

from apps.questions.views.admin.admin_qna_categories_delete_view import (
    AdminCategoryDeleteAPIView,
)
from apps.questions.views.admin.admin_qna_categories_list_view import (
    AdminCategoryAPIView,
)

app_name = "admin_questions"

urlpatterns = [
    # 1. 목록 조회 및 생성
    path(
        "admin/qna/categories/",
        AdminCategoryAPIView.as_view(),
        name="admin-category",
    ),
    # 2. 특정 카테고리 삭제
    path(
        "admin/qna/categories/<int:category_id>/",
        AdminCategoryDeleteAPIView.as_view(),
        name="admin-category-delete",
    ),
]