from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, ValidationError

from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject


class SubjectService:
    COURSE_NOT_FOUND_MESSAGE = "해당 과정을 찾을 수 없습니다."
    SUBJECT_NOT_FOUND_MESSAGE = "과목을 찾을 수 없습니다."
    INVALID_REQUEST_MESSAGE = "유효하지 않은 과목 생성 요청입니다."
    DUPLICATE_SUBJECT_MESSAGE = "동일한 이름의 과목이 이미 존재합니다."

    @staticmethod
    @transaction.atomic
    def create_subject(*, course_id: int, data: dict[str, Any]) -> Subject:
        title = data.get("title")

        if not isinstance(title, str):
            raise ValidationError(detail=SubjectService.INVALID_REQUEST_MESSAGE)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise NotFound(detail=SubjectService.COURSE_NOT_FOUND_MESSAGE)

        if Subject.objects.filter(course=course, title=title).exists():
            raise ValidationError(detail=SubjectService.DUPLICATE_SUBJECT_MESSAGE)

        try:
            return Subject.objects.create(
                course=course,
                title=title,
                number_of_days=data["number_of_days"],
                number_of_hours=data["number_of_hours"],
                thumbnail_img_url=data.get("thumbnail_img_url"),
            )
        except (KeyError, TypeError, IntegrityError):
            raise ValidationError(detail=SubjectService.INVALID_REQUEST_MESSAGE)

    @staticmethod
    def list_subjects_by_course(*, course_id: int) -> QuerySet[Subject]:
        return Subject.objects.select_related("course").filter(course_id=course_id).order_by("id")

    @staticmethod
    def get_subject(*, subject_id: int) -> Subject:
        try:
            return Subject.objects.select_related("course").get(id=subject_id)
        except Subject.DoesNotExist:
            raise NotFound(detail=SubjectService.SUBJECT_NOT_FOUND_MESSAGE)

    @staticmethod
    def get_subject_scatter_queryset(*, subject_id: int) -> QuerySet[ExamSubmission]:
        SubjectService.get_subject(subject_id=subject_id)

        return (
            ExamSubmission.objects.filter(deployment__exam__subject_id=subject_id)
            .exclude(started_at__isnull=True)
            .exclude(created_at__isnull=True)
            .select_related("deployment__exam__subject")
            .order_by("id")
        )
