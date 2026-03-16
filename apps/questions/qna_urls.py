from django.urls import path

from .views.answers_views import AIAnswerViewSet, AnswerViewSet

app_name = "questions"

urlpatterns = [
    # 답변 등록
    path(
        "questions/<int:question_id>/answers",
        AnswerViewSet.as_view({"post": "create"}),
        name="answer_create",
    ),
    # AI 답변 생성/조회
    path(
        "questions/<int:question_id>/ai-answer",
        AIAnswerViewSet.as_view({"get": "retrieve"}),
        name="ai_answer",
    ),
    # 답변 수정
    path(
        "answers/<int:pk>",
        AnswerViewSet.as_view({"put": "update"}),
        name="answer_update",
    ),
    # 답변 채택
    path(
        "answers/<int:pk>/accept",
        AnswerViewSet.as_view({"post": "accept"}),
        name="answer_accept",
    ),
    # 답변 댓글 등록
    path(
        "answers/<int:pk>/comments",
        AnswerViewSet.as_view({"post": "comment"}),
        name="answer_comment_create",
    ),
]
