from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.exam.views.exam_question_views import ExamQuestionViewSet

app_name = "exams"

urlpatterns = [
    path(
        "<int:exam_id>/questions",
        ExamQuestionViewSet.as_view({"post": "create"}),
        name="exam-question-create",
    ),
    path(
        "questions/<int:id>",
        ExamQuestionViewSet.as_view({"put": "update", "delete": "destroy"}),
        name="exam-question-update-delete",
    ),
]
