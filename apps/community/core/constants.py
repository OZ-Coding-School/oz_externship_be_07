import re

POST_VIEW_TTL = 60 * 60  # 1시간
POST_CONTENT_PREVIEW_LENGTH = 50

# 마크다운 이미지/링크 정규식
RE_MARKDOWN_LINK = re.compile(r"(!?)\[(.*?)\]\((https?://[^\s\)]+)\)")
RE_IMAGE_URL = re.compile(r"!\[.*?\]\((https?://[^?)\s]+)(?:\?.*?)?\)")
RE_ATTACHMENT_URL = re.compile(r"(?<!\!)\[(.*?)\]\((https?://[^?)\s]+)(?:\?.*?)?\)")
RE_FILE_URL_STRIP_QS = re.compile(r"(!?)\[(.*?)\]\((https?://[^?)\s]+)(?:\?.*?)?\)")

# url 절취선 기준
RIST_SPLIT = "com/"

# 게시글 수정/추가 필드 옵션 덮기
EXTRA_KWARGS = {
    "title": {
        "error_messages": {
            "blank": "제목은 필수 값입니다.",
        }
    },
    "content": {
        "error_messages": {
            "blank": "내용은 필수 값입니다.",
        }
    },
}

# admin common NUM
ADMIN_COMMENT_PREVIEW_LENGTH = 16
ADMIN_AUTOCOMPLETE_LIMIT = 5

# admin Category delete flow
ADMIN_PREVIEW_LIMIT = 3
ADMIN_DELETE_CONFIRM_TTL_SECONDS = 60
ADMIN_DELETE_CONFIRM_TOKEN_LENGTH = 32

"""
커뮤니티 인사이트 (7 days) -> lms 교육 커뮤니티의 평균 지표를 참조했으며, 초기 감안해 지표수치 전체적으로 하향 
-----------------------------
지표 정의 고정 규칙:
1) user_activation_rate 분모는 LMS 전체 활성 유저(커뮤니티 비참여 포함)
2) response_rate_within_24h 댓글 조건:
   post.created_at <= comment.created_at <= post.created_at + 24h
3) top1_category_share 분모는 active_category_post_counts 합계
4) 모든 지표는 단일 timezone.now() 스냅샷 기준으로 동시에 계산
"""

INSIGHT_WINDOW_DAYS = 7
INSIGHT_RATE_SCALE = 100.0  # 지표는 0~100(%) 스케일

# 24시간 내 응답률 임계값(%)
INSIGHT_RESPONSE_RATE_CRITICAL = 20.0
INSIGHT_RESPONSE_RATE_WARNING = 40.0
INSIGHT_RESPONSE_RATE_GOOD = 60.0

# 신규 유저 정착률 임계값(%)
INSIGHT_SETTLEMENT_RATE_WARNING = 20.0
INSIGHT_SETTLEMENT_RATE_GOOD = 40.0

# 신규 유저 인사이트 제공을 위한 최소 인원
INSIGHT_SETTLEMENT_MIN_USERS = 3

# 게시글당 댓글/좋아요 반응 임계값(개수)
INSIGHT_AVG_COMMENTS_LOW = 0.5
INSIGHT_AVG_COMMENTS_GOOD = 1.5
INSIGHT_AVG_LIKES_LOW = 0.3

# 활성화율 임계값(%)
INSIGHT_ACTIVATION_RATE_GOOD = 10.0
INSIGHT_TARGET_ACTIVATION_RATE = 15.0

# 카테고리 편중 임계값(%)
INSIGHT_TOP1_CATEGORY_SHARE_WARNING = 70.0
INSIGHT_TOP1_CATEGORY_SHARE_CRITICAL = 80.0

# 약한 지표 안내용 목표값(%)
INSIGHT_TARGET_RESPONSE_RATE = 60.0
INSIGHT_TARGET_AVG_COMMENTS = 1.5
INSIGHT_TARGET_SETTLEMENT_RATE = 40.0

# 약한 지표 동률 시 우선순위
INSIGHT_WEAKEST_TIEBREAK_ORDER = (
    "response_rate_within_24h",
    "user_activation_rate",
    "avg_comments_per_post",
    "new_user_settlement_rate",
)
