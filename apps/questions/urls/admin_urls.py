from django.urls import path

from apps.questions.views.admin.admin_qna_answers_delete_view import (
    AdminAnswerDeleteAPIView,
)
from apps.questions.views.admin.admin_qna_categories_delete_view import (
    AdminCategoryDeleteAPIView,
)
from apps.questions.views.admin.admin_qna_categories_list_view import (
    AdminCategoryAPIView,
)
from apps.questions.views.admin.admin_qna_questions_list_view import (
    AdminQuestionDetailAPIView,
)
from apps.questions.views.admin.admin_qna_questions_view import (
    AdminQuestionListAPIView,
)

app_name = "admin_questions"

urlpatterns = [
    # 1. 카테고리 목록 조회 및 생성
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
    # 3. 질의 응답 목록 조회
    path(
        "admin/qna/questions/",
        AdminQuestionListAPIView.as_view(),
        name="admin-question-list",
    ),
    # 4. 질의 응답 상세 조회 및 삭제
    path(
        "admin/qna/questions/<int:question_id>/",
        AdminQuestionDetailAPIView.as_view(),
        name="admin-question-detail",
    ),
    # 5. 답변 삭제
    path(
        "admin/qna/answers/<int:answer_id>/",
        AdminAnswerDeleteAPIView.as_view(),
        name="admin-answer-delete",
    ),
]
