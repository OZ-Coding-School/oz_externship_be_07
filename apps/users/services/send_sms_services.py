from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException, Throttled
from twilio.base.exceptions import TwilioRestException  # type: ignore
from twilio.rest import Client  # type: ignore


class SendSmsService:
    def send_sms_code(self, phone_number: str) -> None:
        clean_number = "".join(filter(str.isdigit, phone_number))
        limit_key = f"limit_sms:{phone_number}"
        if cache.get(limit_key):
            raise Throttled(detail="1분 후에 다시 시도해주세요.")

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            formatted_number = f"+82{clean_number[1:]}"

            client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                to=formatted_number, channel="sms"
            )

            cache.set(limit_key, True, timeout=60)

        except TwilioRestException as e:
            if e.code == 60204:
                raise APIException("Twilio 서비스의 Custom Code 설정 확인이 필요합니다.")
            elif e.code == 60200:
                raise APIException("유효하지 않은 전화번호 형식입니다.")
            else:
                raise APIException(f"SMS 발송 실패: {e.msg} (코드: {e.code})")

        except (ValueError, KeyError, AttributeError):
            raise APIException("설정 및 데이터 형식이 올바르지 않습니다.")
