from django.urls import path

from apps.questions.views.questions_list_views import (
    QuestionListDetailView,
    QuestionListView,
)

app_name = "qna"

urlpatterns = [
    # 질문 등록,조회,수정
    path("api/v1/qna/questions", QuestionListView.as_view(), name="question_list_create"),
    path("api/v1/qna/questions/<int:question_id>/", QuestionListDetailView.as_view(), name="question_detail_update"),
    # path("questiondelete/<int:pk>/", QuestionDeleteView.as_view(), name='question_delete'),
    # 답변 관련
]
