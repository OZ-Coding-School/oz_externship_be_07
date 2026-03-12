import random

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail


class EmailVerificationService:
    def create_code(self) -> str:
        """6자리 숫자 번호 만들기"""
        return str(random.randint(100000, 999999))

    def send_verification_code(self, email: str) -> None:
        """번호 생성 -> Redis 저장 -> 이메일 발송"""
        code = self.create_code()

        # Redis에 'verify:이메일' 이름으로 5분간 저장
        cache.set(f"verify:{email}", code, timeout=300)

        # 실제 이메일 발송
        subject = "[OZ] 이메일 인증 코드"
        message = f"인증 코드는 [{code}] 입니다."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
