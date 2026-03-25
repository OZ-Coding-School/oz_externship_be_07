from django.urls import path

from apps.questions.views.admin.admin_qna_categories_list_view import (
    AdminCategoryAPIView,
)
from apps.questions.views.admin.admin_qna_categories_views import (
    AdminCategoryCreateAPIView,
)

app_name = "admin_questions"

urlpatterns = [
    path("categories/", AdminCategoryAPIView.as_view(), name="admin-category"),
]
