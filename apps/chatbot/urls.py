from django.urls import path

from apps.chatbot.views import (
    ChatbotCompletionListCreateView,
    ChatbotSessionDetailView,
    ChatbotSessionListCreateView,
    ChatbotSupportView,
)

app_name = "chatbot"

urlpatterns = [
    # QnA 챗봇
    path("sessions/", ChatbotSessionListCreateView.as_view(), name="session-list-create"),
    path("sessions/<int:session_id>/", ChatbotSessionDetailView.as_view(), name="session-detail"),
    path(
        "sessions/<int:session_id>/completions/",
        ChatbotCompletionListCreateView.as_view(),
        name="session-completions",
    ),
    # CS 상담 챗봇
    path("support/", ChatbotSupportView.as_view(), name="support"),
]
