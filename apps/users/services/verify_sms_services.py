import secrets

from django.conf import settings
from django.core.cache import cache
from twilio.rest import Client  # type: ignore


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
            cache.set(f"sms_token:{sms_token}", phone_number, timeout=300)

            return sms_token

        except ValueError:
            raise

        except Exception as e:
            error_msg = str(e).lower()

            if "not found" in error_msg or "invalid" in error_msg:
                raise ValueError("인증번호가 올바르지 않습니다.")

            raise RuntimeError(f"SMS 서비스 일시적 오류: {str(e)}")
