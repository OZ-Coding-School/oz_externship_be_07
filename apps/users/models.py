from django.db import models

from apps.core.models import TimeStampModel

from .choices import SocialProvider, UserGender, UserRole, WithdrawalReason


# 사용자 테이블
class User(TimeStampModel):
    email = models.EmailField(max_length=255, unique=True, verbose_name="이메일")
    hashed_password = models.CharField(max_length=130, verbose_name="비밀번호")
    name = models.CharField(max_length=30, verbose_name="이름")
    nickname = models.CharField(max_length=10, unique=True, verbose_name="닉네임")
    phone_number = models.CharField(max_length=20, unique=True, verbose_name="휴대폰번호")
    gender = models.CharField(max_length=6, choices=UserGender, verbose_name="성별")
    birthday = models.DateField(verbose_name="생년월일")
    profile_img_url = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    role = models.CharField(max_length=10, choices=UserRole, default="User", verbose_name="역할")

    class Meta:
        db_table = "user"


# 소셜 유저 테이블
class SocialUser(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=10, choices=SocialProvider)
    provider_id = models.CharField(max_length=255)

    class Meta:
        db_table = "social_users"


# 탈퇴 정보 테이블
class Withdrawal(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="withdrawals")
    reason = models.CharField(max_length=50, choices=WithdrawalReason)
    reason_detail = models.TextField()
    due_date = models.DateField()

    class Meta:
        db_table = "withdrawals"
