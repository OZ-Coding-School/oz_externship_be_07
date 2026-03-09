from django.db import models


class Course(models.Model):

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        max_length=30,
        unique=True
    )

    tag = models.CharField(
        max_length=3,
        unique=True
    )

    description = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    thumbnail_img_url = models.URLField(
        max_length=255,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )