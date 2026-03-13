import secrets
import string

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.exceptions import APIException, Throttled


class SendEmailService:
    def create_code(self) -> str:
        return "".join(secrets.choice(string.digits) for _ in range(6))

    def send_email_code(self, email: str) -> None:
        limit_key = f"limit:{email}"
        verify_key = f"verify:{email}"

        if cache.get(limit_key):
            raise Throttled(detail="1분 후에 다시 시도해주세요.")

        code = self.create_code()

        try:
            subject = "[OZ] 이메일 인증 코드"
            message = f"요청하신 인증코드는 {code} 입니다."
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            cache.set(verify_key, code, timeout=300)
            cache.set(limit_key, True, timeout=60)
        except Exception:
            raise APIException("이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요.")
