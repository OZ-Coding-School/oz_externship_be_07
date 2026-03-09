from django.db import models


class UserRole(models.TextChoices):
    USER = ("USER",)
    STUDENT = ("STUDENT",)
    TA = ("TA",)
    OM = ("OM",)
    ADMIN = ("ADMIN",)


class UserGender(models.TextChoices):
    MALE = ("MALE",)
    FEMALE = "FEMALE"


class SocialProvider(models.TextChoices):
    KAKAO = "kakao"
    NAVER = "naver"


class WithdrawalReason(models.TextChoices):
    GRADUATION = "GRADUATION", "수강완료"
    TRANSFER = "TRANSFER", "타 부트캠프에 더 양질의 컨텐츠가 있어서"
    NO_LONGER_NEEDED = "NO_LONGER_NEEDED", "더 이상 필요가 없어서"
    SERVICE_DISSATISFACTION = "SERVICE_DISSATISFACTION", "사이트내 UX/UI가 불편해서"
    PRIVACY_CONCERN = "PRIVACY_CONCERN", "개인정보 우려 "
    OTHER = "OTHER", "기타(직접입력)"
