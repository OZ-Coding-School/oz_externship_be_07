import secrets
import string

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException, Throttled
from twilio.rest import Client  # type: ignore


class SendSmsService:
    def create_code(self) -> str:
        return "".join(secrets.choice(string.digits) for _ in range(6))

    def send_sms_code(self, phone_number: str) -> None:
        limit_key = f"limit_sms:{phone_number}"
        verify_key = f"verify_sms:{phone_number}"

        if cache.get(limit_key):
            raise Throttled(detail="1분 후에 다시 시도해주세요.")

        code = self.create_code()

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            formatted_number = f"+82{phone_number[1:]}"

            client.messages.create(
                body=f"[OZ] 인증번호 [{code}]를 입력해주세요.", from_=settings.TWILIO_PHONE_NUMBER, to=formatted_number
            )

            cache.set(verify_key, code, timeout=300)
            cache.set(limit_key, code, timeout=60)

        except ValueError:
            raise APIException("SMS 발송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
