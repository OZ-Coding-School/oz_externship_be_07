from django.conf import settings
from django.core.cache import cache
from twilio.rest import Client  # type: ignore

from apps.users.constants import RATE_LIMIT_TIMEOUT


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
