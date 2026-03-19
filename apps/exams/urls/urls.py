from django.urls import path

from apps.exams.views.exam_question_views import (
    ExamQuestionCreateAPIView,
    ExamQuestionUpdateDeleteAPIView,
)

app_name = "exams"

urlpatterns = [
    path("<int:exam_id>/questions", ExamQuestionCreateAPIView.as_view(), name="exams-question-create"),
    path("questions/<int:question_id>", ExamQuestionUpdateDeleteAPIView.as_view(), name="exam_question-update-delete"),
]
