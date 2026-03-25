from django.urls import path

from apps.questions.views.admin.admin_qna_categories_list_view import (
    AdminCategoryAPIView,
)

app_name = "admin_questions"

urlpatterns = [
    path("admin/qna/categories/", AdminCategoryAPIView.as_view(), name="admin-category"),
]
