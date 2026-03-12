from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    # 챗봇 세션 생성, 챗봇 세션 목록 조회
    path("sessions", views.ChatbotSessionListCreateView.as_view(), name="session-list-create"),
    
    # 시스템 (고객지원) 챗봇 세션 생성
    path('support', views.ChatbotSupportCreateView.as_view(), name='session-support-create'),
    
    # 챗봇 세션 삭제
    path('sessions/<int:session_id>', views.ChatbotSessionDetailView.as_view(), name='session-detail'),
    
    # AI 답변 생성, 대화내역 조회, 초기화
    path('sessions/<int:session_id>/completions', views.ChatbotCompletionView.as_view(), name='session-completions'),
]
