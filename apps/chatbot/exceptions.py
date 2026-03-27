class ChatbotServiceError(Exception):
    """챗봇 서비스에서 발생하는 모든 예외의 최상위 부모 클래스"""

    pass


class SessionNotFoundError(ChatbotServiceError):
    """사용자의 챗봇 세션을 찾을 수 없을 때 발생하는 예외 (HTTP 404 매핑 용도)"""

    pass


class AIModelConnectionError(ChatbotServiceError):
    """AI 모델과의 통신 중 문제가 있을 때 발생하는 예외 (HTTP 502 매핑 용도)"""

    pass


class ChatbotThrottledError(ChatbotServiceError):
    """Redis Lock이 걸려있어 동시 요청이 차단되었을 때 발생하는 예외 (HTTP 429 매핑 용도)"""

    pass


class InvalidSessionStateError(ChatbotServiceError):
    """세션은 존재하지만 현재 대화를 이어갈 수 없는 상태일 때 발생하는 예외 (HTTP 400 매핑 용도)"""

    pass


class MissingQuestionContextError(ChatbotServiceError):
    """QnA 챗봇에서 참조해야 할 원본 질문글이 DB에서 삭제되었을 때 발생하는 예외 (HTTP 404 매핑 용도)"""

    pass
