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
