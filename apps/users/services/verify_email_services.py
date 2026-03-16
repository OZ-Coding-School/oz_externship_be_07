import base64
import secrets

from django.core.cache import cache
from rest_framework.exceptions import ValidationError


class EmailVerifyService:
    def verify_email_code(self, email: str, code: str) -> str:
        verify_key = f"verify:{email}"
        fail_key = f"failure_count:{email}"

        verify_code = cache.get(verify_key)

        if not verify_code:
            raise ValidationError("인증 시간이 만료되었거나 잘못된 요청입니다.")

        if verify_code != code:
            fail_count = cache.get(fail_key, 0) + 1

            if fail_count >= 5:
                cache.delete(verify_key)
                cache.delete(fail_key)
                raise ValidationError("인증 번호 5회 실패로 인증이 취소되었습니다. 다시 인증번호를 요청해주세요.")

            cache.set(fail_key, fail_count, timeout=300)
            raise ValidationError(f"인증번호가 일치하지 않습니다. (남은 횟수: {5 - fail_count}회)")

        cache.delete(verify_key)
        cache.delete(fail_key)

        random_bytes = secrets.token_bytes(20)
        email_token = base64.b32encode(random_bytes).decode("utf-8")

        token_key = f"email_token:{email_token}"
        cache.set(token_key, email, timeout=3600)

        return email_token
