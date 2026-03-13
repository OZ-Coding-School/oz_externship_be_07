from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from apps.core.models import TimeStampModel
from apps.users.choices import (
    SocialProvider,
    UserGender,
    UserRole,
    UserStatus,
    WithdrawalReason,
)


class UserManager(BaseUserManager["User"]):
    def create_user(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        return self.create_user(email, password, **extra_fields)


# 사용자 테이블
class User(AbstractBaseUser, PermissionsMixin, TimeStampModel):
    password = models.CharField(max_length=128, default="", verbose_name="비밀번호")
    email = models.EmailField(max_length=255, unique=True, verbose_name="이메일")
    name = models.CharField(max_length=30, verbose_name="이름")
    nickname = models.CharField(max_length=10, unique=True, verbose_name="닉네임")
    phone_number = models.CharField(max_length=20, unique=True, verbose_name="휴대폰번호")
    gender = models.CharField(max_length=6, choices=UserGender, verbose_name="성별")
    birthday = models.DateField(verbose_name="생년월일")
    profile_img_url = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(choices=UserStatus, default=UserStatus.ACTIVATED)
    role = models.CharField(max_length=10, choices=UserRole, default=UserRole.USER, verbose_name="권한")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "name",
        "phone_number",
        "gender",
        "birthday",
    ]

    class Meta:
        db_table = "user"


# 소셜 유저 테이블
class SocialUser(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=10, choices=SocialProvider)
    provider_id = models.CharField(max_length=255)

    class Meta:
        db_table = "social_users"
        constraints = [
            models.UniqueConstraint(fields=["user", "provider"], name="unique_social_account"),
        ]


# 탈퇴 정보 테이블
class Withdrawal(TimeStampModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="withdrawals")
    reason = models.CharField(max_length=50, choices=WithdrawalReason)
    reason_detail = models.TextField()
    due_date = models.DateField()

    class Meta:
        db_table = "withdrawals"
