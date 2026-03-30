import base64
import secrets
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework.exceptions import APIException, Throttled, ValidationError
from twilio.rest import Client  # type: ignore

from apps.users.constants import (
    FAIL_COUNT_TIMEOUT,
    MAX_VERIFY_ATTEMPTS,
    RATE_LIMIT_TIMEOUT,
    SMS_TOKEN_TIMEOUT,
    TOKEN_TIMEOUT,
    VERIFICATION_CODE_TIMEOUT,
)

User = get_user_model()


class SendEmailService:
    def create_code(self) -> str:
        charset = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return "".join(secrets.choice(charset) for _ in range(6))

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

            cache.set(verify_key, code, timeout=VERIFICATION_CODE_TIMEOUT)
            cache.set(limit_key, True, timeout=RATE_LIMIT_TIMEOUT)
        except Exception:
            raise APIException("이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요.")


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


class SendSmsService:
    def send_sms_code(self, phone_number: str) -> None:
        clear_number = "".join(filter(str.isdigit, phone_number))
        limit_key = f"limit_sms:{phone_number}"

        if cache.get(limit_key):
            raise ValueError("1분 후에 다시 시도해주세요.")

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            formatted_number = f"+82{clear_number[1:]}"

            client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                to=formatted_number, channel="sms"
            )

            cache.set(limit_key, True, timeout=RATE_LIMIT_TIMEOUT)

        except Exception:
            raise RuntimeError("인증번호 발송 중 오류가 발생했습니다.")


class VerifySmsService:
    def verify_code(self, phone_number: str, code: str) -> str:
        formatted_number = f"+82{phone_number[1:]}"
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            verify_check = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
                to=formatted_number, code=code
            )

            if verify_check.status != "approved":
                raise ValueError("인증번호가 올바르지 않습니다.")

            sms_token = secrets.token_urlsafe(32)
            cache.set(f"sms_token:{sms_token}", phone_number, timeout=SMS_TOKEN_TIMEOUT)

            return sms_token

        except Exception as e:
            error_msg = str(e).lower()

            if "not found" in error_msg or "invalid" in error_msg:
                raise ValueError("인증번호가 올바르지 않습니다.")

            raise RuntimeError(f"SMS 서비스 일시적 오류: {str(e)}")
