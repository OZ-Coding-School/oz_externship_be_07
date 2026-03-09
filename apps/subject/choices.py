from django.db import models


class CohortStatus(models.TextChoices):
    START = "START"
    READY = "READY"
    END = "END"


class StudentEnrollmentRequestsStatus(models.TextChoices):
    REJECT = "REJECT"
    PENDING = "PENDING"
    ALLOW = "ALLOW"
