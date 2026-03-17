from django.db import models


class QuestionType(models.TextChoices):
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    OX = "OX"
    SHORT_ANSWER = "SHORT_ANSWER"
    ORDERING = "ORDERING"
    FULL_BLANK = "FULL_BLANK"


class DeploymentStatus(models.TextChoices):
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"
    CLOSED = "CLOSED"
