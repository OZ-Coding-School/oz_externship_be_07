from django.urls import path

from apps.exam.views.exam_question_views import (
    ExamQuestionDetailAPIView,
    ExamQuestionListCreateAPIView,
)

app_name = "exam"

urlpatterns = [
    path("<int:exam_id>/questions", ExamQuestionListCreateAPIView.as_view(), name="exam-question-list-create"),
    path("questions/<int:question_id>", ExamQuestionDetailAPIView.as_view(), name="exam_question-detail"),
]
