from django.urls import path

from .views.answers_views import AnswerViewSet

app_name = "questions"

urlpatterns = [
    # 답변 등록: POST /api/v1/qna/questions/{question_id}/answers
    path(
        "api/v1/qna/questions/<int:question_id>/answers",
        AnswerViewSet.as_view({"post": "create"}),
        name="answer_create",
    ),
    # AI 답변 생성: GET /api/v1/qna/questions/{question_id}/ai-answer
    path(
        "api/v1/qna/questions/<int:question_id>/ai-answer",
        AnswerViewSet.as_view({"get": "get_ai_answer"}),
        name="ai_answer",
    ),
    # 답변 수정: PUT /api/v1/qna/answers/{answer_id}
    path("api/v1/qna/answers/<int:pk>", AnswerViewSet.as_view({"put": "update"}), name="answer_update"),
    # 답변 채택: POST /api/v1/qna/answers/{answer_id}/accept
    path("api/v1/qna/answers/<int:pk>/accept", AnswerViewSet.as_view({"post": "accept"}), name="answer_accept"),
    # 답변 댓글 작성: POST /api/v1/qna/answers/{answer_id}/comments
    path(
        "api/v1/qna/answers/<int:pk>/comments", AnswerViewSet.as_view({"post": "comment"}), name="answer_comment_create"
    ),
]
