from django.db import models


class CohortStatus(models.TextChoices):
    PREPARING = "PREPARING"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class StudentEnrollmentRequestsStatus(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"


class SubjectStatus(models.TextChoices):
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"
