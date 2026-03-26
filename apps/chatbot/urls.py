from django.urls import path

from . import views
from .views import (
    ChatbotCompletionView,
    ChatbotSessionDetailView,
    ChatbotSessionListCreateView,
    ChatbotSupportCreateView,
)

app_name = "chatbot"

urlpatterns = [
    # QnA 챗봇
    path("sessions", views.ChatbotSessionListCreateView.as_view(), name="session-list-create"),
    path("sessions/<int:session_id>", views.ChatbotSessionDetailView.as_view(), name="session-detail"),
    path("sessions/<int:session_id>/completions", views.ChatbotCompletionView.as_view(), name="session-completions"),
    # CS 챗봇
    path("support", views.ChatbotSupportCreateView.as_view(), name="session-support-create"),
]
