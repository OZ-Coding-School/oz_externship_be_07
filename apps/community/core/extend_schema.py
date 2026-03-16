from typing import Any

from drf_spectacular.utils import OpenApiExample


def extend_schema(name: str, value: dict[str, Any], status_code: str) -> OpenApiExample:

    return OpenApiExample(
        name,
        value,
        status_codes=[status_code],
        response_only=True,
    )


value_list = {
    "200": extend_schema(
        "Ok", {"id": 1, "title": "수정된 게시글 본문입니다. 마크다운 허용", "category": "테스트 게시판"}, "200"
    ),
    "200_delete": extend_schema("Ok", {"detail": "게시글이 삭제되었습니다."}, "200"),
    "201": extend_schema("Created", {"detail": "게시글이 성공적으로 등록되었습니다.", "pk": 1}, "201"),
    "400": extend_schema("Bad Request", {"error_detail": {"title": ["이 필드는 필수 항목입니다."]}}, "400"),
    "401": extend_schema("Unauthorized", {"error_detail": "자격 인증 데이터가 제공되 않았습니다."}, "401"),
    "403": extend_schema("Forbidden", {"error_detail": "권한이 없습니다."}, "403"),
    "404": extend_schema("Not Found", {"error_detail": "해당 게시글을 찾을 수 없습니다."}, "404"),
}
