from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.exceptions import ValidationError

User = get_user_model()


class FindEmailService:
    @staticmethod
    def verify_sms_token(name: str, sms_token: str) -> str:
        cache_key = f"sms_token:{sms_token}"
        phone_number = cache.get(cache_key)

        if not phone_number:
            raise ValidationError({"sms_token": ["휴대폰 인증 실패 - 인증 토큰이 유효하지 않거나 만료되었습니다."]})

        try:
            user = User.objects.get(name=name, phone_number=phone_number)
            cache.delete(cache_key)

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
