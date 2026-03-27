from rest_framework.pagination import CursorPagination


class ChatbotCursorPagination(CursorPagination):
    """챗봇 세션/대화내역 커서 기반 페이지네이션"""

    page_size = 10
    page_size_query_param = "page_size"
    ordering = "-created_at"
