from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from twilio.rest import Client  # type: ignore

User = get_user_model()


class FindEmailService:
    @staticmethod
    def find_email(name: str, phone_number: str, code: str) -> str:
        formatted_number = f"+82{phone_number[1:]}"

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            verify_check = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
                to=formatted_number, code=code
            )
            if verify_check.status != "approved":
                raise ValidationError({"code": ["인증번호가 올바르지 않습니다."]})
        except ValidationError:
            raise
        except Exception:
            raise ValidationError({"code": ["인증번호가 올바르지 않거나 만료되었습니다."]})

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
