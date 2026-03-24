# apps/questions/urls/admin_urls.py
from django.urls import path

from apps.questions.views.admin.admin_qna_categories_list_view import (
    AdminCategoryListAPIView,
)
from apps.questions.views.admin.admin_qna_categories_views import (
    AdminCategoryCreateAPIView,
)

app_name = "admin_questions"

urlpatterns = [
    # Admin_qna_category 등록 및 조회
    path(
        "admin/qna/categories/create/",
        AdminCategoryCreateAPIView.as_view(),
        name="admin_category_create",
    ),
    path(
        "admin/qna/categories/list/",
        AdminCategoryListAPIView.as_view(),
        name="admin_category_list",
    ),
]
