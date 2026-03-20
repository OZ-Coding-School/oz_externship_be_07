from rest_framework.response import Response


def error_response(*, message: str, http_status: int) -> Response:
    return Response({"error_detail": message}, status=http_status)
