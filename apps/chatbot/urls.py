from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("sessions", views.ChatbotSessionListCreateView.as_view(), name="session-list-create"),
    path('support', views.ChatbotSupportCreateView.as_view(), name='session-support-create'),
    path('sessions/<int:session_id>', views.ChatbotSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<int:session_id>/completions', views.ChatbotCompletionView.as_view(), name='session-completions'),
]
