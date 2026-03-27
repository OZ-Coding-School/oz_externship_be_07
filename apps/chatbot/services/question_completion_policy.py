import re

from rest_framework.exceptions import ValidationError

MAX_INPUT_LENGTH = 1000

BLOCKED_PROMPT_KEYWORDS = [
    "시스템 프롬프트",
    "system prompt",
    "developer message",
    "hidden prompt",
    "prompt reveal",
    "프롬프트 보여줘",
    "프롬프트 공개",
    "너의 지침",
    "너의 규칙",
    "규칙을 보여줘",
    "정책을 보여줘",
    "policy",
    "content policy",
    "지시를 무시",
    "이전 지시 무시",
    "ignore instructions",
    "disregard",
    "override",
    "역할을 바꿔",
    "roleplay",
    "act as",
    "너는 이제",
    "탈옥",
    "jailbreak",
    "prompt injection",
    "dan",
    "temperature",
    "top_p",
    "system message",
    "api key",
    "secret key",
    "키를 알려줘",
    "토큰",
    "모델 뭐야",
    "사용하는 모델",
    "gpt",
    "gemini",
    "claude",
    "llama",
    "openai",
]

BLOCKED_NONQUESTION_KEYWORDS = [
    "소설",
    "시나리오",
    "대본",
    "웹소설",
    "스토리",
    "창작해줘",
    "시 써줘",
    "가사 써줘",
    "번역해줘",
    "번역해줘요",
    "요약해줘",
    "요약해줘요",
    "광고 문구",
    "마케팅 문구",
    "홍보 글",
]

BLOCKED_BUILD_REQUEST_KEYWORDS = [
    "프로그램 만들어줘",
    "앱 만들어줘",
    "웹 만들어줘",
    "서비스 만들어줘",
    "완성해줘",
    "전체 코드",
    "풀코드",
    "통파일로",
    "프로젝트 통째로",
    "배포까지",
    "운영 가능한",
]

BLOCKED_SUPPORT_LIKE_KEYWORDS = [
    "출결",
    "결석",
    "지각",
    "출석",
    "과제",
    "제출",
    "계정",
    "로그인",
    "비밀번호",
    "수강 신청",
    "수강신청",
    "결제",
    "환불",
    "운영",
    "관리자",
    "정책",
    "문의",
]

_NORMALIZE_RE = re.compile(r"[\s\W_]+", re.UNICODE)


def _normalize_text(content: str) -> str:
    return _NORMALIZE_RE.sub("", content.lower())


def validate_question_input(content: str) -> None:
    """QnA 챗봇 입력 검증 (프롬프트 인젝션 + 도메인 필터링)"""
    _validate_input_content(content)
    _validate_prompt_injection(content)
    _validate_question_domain(content)


def _validate_input_content(content: str) -> None:
    if not content or not content.strip():
        raise ValidationError("질문 내용을 입력해 주세요.")
    if len(content) > MAX_INPUT_LENGTH:
        raise ValidationError("질문은 최대 1000자까지 입력할 수 있습니다.")


def _validate_prompt_injection(content: str) -> None:
    raw_lower = content.lower()
    normalized = _normalize_text(content)

    for keyword in BLOCKED_PROMPT_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("해당 요청은 처리할 수 없습니다.")


def _validate_question_domain(content: str) -> None:
    raw_lower = content.lower()
    normalized = _normalize_text(content)

    for keyword in BLOCKED_SUPPORT_LIKE_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("해당 문의는 고객지원 챗봇을 통해 안내받을 수 있습니다.")

    for keyword in BLOCKED_NONQUESTION_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("질문하기에서는 학습 질문에 대해서만 답변할 수 있습니다.")

    for keyword in BLOCKED_BUILD_REQUEST_KEYWORDS:
        k1 = keyword.lower()
        k2 = _NORMALIZE_RE.sub("", k1)
        if k1 in raw_lower or (k2 and k2 in normalized):
            raise ValidationError("질문하기에서는 완성형 제작 요청이 아니라 학습 질문 위주로 도와드릴 수 있습니다.")
