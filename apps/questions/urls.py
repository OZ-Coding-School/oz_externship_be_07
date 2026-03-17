from django.urls import path

from apps.questions.views.questions_create_views import QuestionCreateView
from apps.questions.views.questions_list_views import (
    QuestionListDetailView,
    QuestionListView,
)

app_name = "qna"

urlpatterns = [
    # 질문 등록,조회,수정
    path("questions/", QuestionListView.as_view(), name="question_list_create"),
    path("questions/<int:question_id>/", QuestionListDetailView.as_view(), name="question_detail"),
    # 답변 관련
]
