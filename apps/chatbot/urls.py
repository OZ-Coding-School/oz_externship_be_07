from django.urls import path

from . import views
from .views import ChatbotCompletionView

app_name = "chatbot"

urlpatterns = [
    # 챗봇 세션 생성
    path("sessions", views.ChatbotSessionCreateView.as_view(), name="session-create"),
    # 대화시작, 내역 조회
    path(
        "<str:bot_type>/sessions/<str:session_id>/completions",
        views.ChatbotCompletionView.as_view(),
        name="chatbot-completions",
    ),
]
