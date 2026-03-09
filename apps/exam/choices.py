from django.db import models


class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    OX = "OX"
    FULL_BLANK = "FULL_BLANK"


class DeploymentStatus(models.TextChoices):
    ACTIVEED = "ACTIVEED"
    DEACTIVATED = "DEACTIVATED"
