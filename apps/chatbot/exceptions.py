class ChatbotServiceError(Exception):
    """챗봇 서비스에서 발생하는 모든 예외의 최상위 부모 클래스"""

    pass


class SessionNotFoundError(ChatbotServiceError):
    """사용자의 챗봇 세션을 찾을 수 없을 때 발생하는 예외"""

    pass


class AIModelConnectionError(ChatbotServiceError):
    """AI 모델과의 통신 중 문제가 있을 때 발생하는 예외"""

    pass
