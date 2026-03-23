import base64
import secrets

from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from apps.users.constants import FAIL_COUNT_TIMEOUT, MAX_VERIFY_ATTEMPTS, TOKEN_TIMEOUT


class EmailVerifyService:
    def verify_email_code(self, email: str, code: str) -> str:
        verify_key = f"verify:{email}"
        fail_key = f"failure_count:{email}"

        fail_count = cache.get(fail_key, 0)

        if fail_count >= MAX_VERIFY_ATTEMPTS:
            raise ValidationError(f"인증 번호 {MAX_VERIFY_ATTEMPTS}회 실패. 다시 인증번호를 요청해주세요.")

        verify_code = cache.get(verify_key)

        if not verify_code:
            raise ValidationError("인증 시간이 만료되었거나 잘못된 요청입니다.")

        if verify_code != code:
            fail_count += 1
            cache.set(fail_key, fail_count, timeout=FAIL_COUNT_TIMEOUT)

            if fail_count >= MAX_VERIFY_ATTEMPTS:
                cache.delete(verify_key)
                raise ValidationError(f"인증 번호 {MAX_VERIFY_ATTEMPTS}회 실패. 다시 인증번호를 요청해주세요.")

            raise ValidationError(f"인증번호가 일치하지 않습니다. (남은 횟수: {MAX_VERIFY_ATTEMPTS - fail_count}회)")

        cache.delete(verify_key)
        cache.delete(fail_key)

        random_bytes = secrets.token_bytes(20)
        email_token = base64.b32encode(random_bytes).decode("utf-8")

        token_key = f"email_token:{email_token}"
        cache.set(token_key, email, timeout=TOKEN_TIMEOUT)

        return email_token
