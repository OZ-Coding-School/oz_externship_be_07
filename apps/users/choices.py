from django.db import models


class UserRole(models.TextChoices):
    USER = (
        "USER",
        "일반 회원",
    )
    STUDENT = (
        "STUDENT",
        "수강생",
    )
    TA = (
        "TA",
        "강사님",
    )
    OM = (
        "OM",
        "운영 매니저",
    )
    ADMIN = (
        "ADMIN",
        "관리자",
    )


class UserGender(models.TextChoices):
    MALE = (
        "MALE",
        "남자",
    )
    FEMALE = ("FEMALE", "여자")


class SocialProvider(models.TextChoices):
    KAKAO = (
        "kakao",
        "KAKAO",
    )
    NAVER = (
        "naver",
        "NAVER",
    )


class WithdrawalReason(models.TextChoices):
    GRADUATION = "GRADUATION", "수강완료"
    TRANSFER = "TRANSFER", "타 부트캠프에 더 양질의 컨텐츠가 있어서"
    NO_LONGER_NEEDED = "NO_LONGER_NEEDED", "더 이상 필요가 없어서"
    SERVICE_DISSATISFACTION = "SERVICE_DISSATISFACTION", "사이트내 UX/UI가 불편해서"
    PRIVACY_CONCERN = "PRIVACY_CONCERN", "개인정보 우려 "
    OTHER = "OTHER", "기타(직접입력)"
