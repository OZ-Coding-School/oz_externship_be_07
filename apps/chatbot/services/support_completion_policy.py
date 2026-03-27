from rest_framework.exceptions import ValidationError

MAX_INPUT_LENGTH = 1000

BLOCKED_PROMPT_KEYWORDS = [
    "시스템 프롬프트",
    "system prompt",
    "developer message",
    "hidden prompt",
    "프롬프트 보여줘",
    "프롬프트 공개",
    "너의 규칙",
    "너의 지침",
    "정책을 보여줘",
    "prompt",
    "지시를 무시",
    "이전 지시 무시",
    "ignore instructions",
    "override",
    "역할을 바꿔",
    "roleplay",
    "act as",
    "너는 이제",
    "탈옥",
    "jailbreak",
    "prompt injection",
    "dan",
    "api key",
    "secret key",
    "키를 알려줘",
    "토큰",
    "temperature",
    "top_p",
    "gpt",
    "gemini",
    "claude",
    "llama",
    "사용하는 모델",
    "모델 뭐야",
]

BLOCKED_SUPPORT_KEYWORDS = [
    "코드 짜줘",
    "프로그램 만들어줘",
    "앱 만들어줘",
    "웹 만들어줘",
    "알고리즘",
    "구현해줘",
    "소설 써줘",
    "시 써줘",
    "대본 써줘",
    "번역해줘",
    "요약해줘",
    "왜 그런지",
    "개념 설명",
    "문제 풀어줘",
    "로직 설명",
]


def validate_support_input(content: str) -> None:
    """CS 상담 챗봇 입력 검증 (프롬프트 인젝션 + 도메인 필터링)"""
    _validate_input_content(content)
    _validate_prompt_injection(content)
    _validate_support_domain(content)


def _validate_input_content(content: str) -> None:
    if not content or not content.strip():
        raise ValidationError("질문 내용을 입력해 주세요.")
    if len(content) > MAX_INPUT_LENGTH:
        raise ValidationError("질문이 너무 깁니다. 내용을 줄여 주세요.")


def _validate_prompt_injection(content: str) -> None:
    lowered = content.lower()
    for keyword in BLOCKED_PROMPT_KEYWORDS:
        if keyword.lower() in lowered:
            raise ValidationError("해당 요청은 처리할 수 없습니다.")


def _validate_support_domain(content: str) -> None:
    lowered = content.lower()
    for keyword in BLOCKED_SUPPORT_KEYWORDS:
        if keyword.lower() in lowered:
            raise ValidationError("고객지원 채팅에서는 서비스 이용 관련 문의만 가능합니다.")
