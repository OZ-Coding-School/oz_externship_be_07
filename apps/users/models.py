from django.db import models

from apps.core.models import BaseModel


# 사용자 테이블
class User(BaseModel):
    # BIGINT + PK = Django -> BigAutoField
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True, verbose_name="이메일")
    hashed_password = models.CharField(max_length=130, verbose_name="비밀번호")
    name = models.CharField(max_length=30, verbose_name="이름")
    nickname = models.CharField(max_length=10, unique=True, verbose_name="닉네임")
    phone_number = models.CharField(max_length=20, unique=True, verbose_name="휴대폰번호")
    gender = models.CharField(max_length=6, verbose_name="성별")
    birthday = models.DateField(verbose_name="생년월일")
    profile_img_url = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ("U", "User"),  # 일반회원
        ("ST", "Student"),  # 수강생
        ("TA", "Teaching Assistant"),  # 강사님
        ("OM", "Operation Manager"),  # 운영 매니저
        ("ADMIN", "Administrator"),  # 관리자
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="User", verbose_name="역할")

    class Meta:
        db_table = "user"


# 소셜 유저 테이블
class SocialUser(BaseModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=50)  # KAKAO, NAVER 등
    provider_id = models.CharField(max_length=255)

    class Meta:
        db_table = "social_users"


# 탈퇴 정보 테이블
class Withdrawal(BaseModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="withdrawals")
    reason = models.CharField(max_length=50)
    reason_detail = models.TextField()
    due_date = models.DateField()

    class Meta:
        db_table = "withdrawals"
