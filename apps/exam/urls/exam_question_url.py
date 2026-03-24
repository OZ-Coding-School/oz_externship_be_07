from django.urls import path

from apps.exam.views.exam_question_views import (
    ExamQuestionCreateAPIView,
    ExamQuestionUpdateDeleteAPIView,
)

urlpatterns = [
    path(
        "<int:exam_id>/questions",
        ExamQuestionCreateAPIView.as_view(),
        name="exam-question-create",
    ),
    path(
        "questions/<int:id>",
        ExamQuestionUpdateDeleteAPIView.as_view(),
        name="exam-question-update-delete",
    ),
]
