from typing import Any

from rest_framework_simplejwt.tokens import RefreshToken


class ReTokenService:
    def refresh_access_token(self, refresh_token: str) -> str:
        refresh = RefreshToken(refresh_token)  # type: ignore
        return str(refresh.access_token)
