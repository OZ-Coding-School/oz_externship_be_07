from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from apps.users.services.send_sms_services import SendSmsService
from apps.users.services.verify_sms_services import VerifySmsService

User = get_user_model()


class FindEmailService:
    @staticmethod
    def send_verification_sms(name: str, phone_number: str) -> None:
        if not User.objects.filter(name=name, phone_number=phone_number).exists():
            raise ValidationError({"non_field_errors": ["일치하는 사용자 정보가 없습니다."]})

        SendSmsService().send_sms_code(phone_number=phone_number)

    @staticmethod
    def verify_sms_code(name: str, phone_number: str, code: str) -> str:
        is_verified = VerifySmsService().verify_code(phone_number=phone_number, code=code)

        if not is_verified:
            raise ValidationError({"code": ["휴대폰 인증 실패 - 인증코드가 유효하지 않습니다."]})
        try:
            user = User.objects.get(name=name, phone_number=phone_number)
            return FindEmailService.mask_email(str(user.email))
        except User.DoesNotExist:
            raise ValidationError({"non_field_errors": ["일치하는 사용자 정보가 없습니다."]})

    @staticmethod
    def mask_email(email: str) -> str:
        try:
            user_part, domain_part = email.split("@")
            masked_user = user_part[0] + "**" + user_part[-1] if len(user_part) > 2 else user_part[0] + "**"

            domain_name, extension = domain_part.split(".", 1)
            masked_domain = (
                domain_name[0] + "****" + domain_name[-1] if len(domain_name) > 2 else domain_name[0] + "****"
            )

            return f"{masked_user}@{masked_domain}.{extension}"
        except Exception:
            return email
