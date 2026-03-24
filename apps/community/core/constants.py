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
