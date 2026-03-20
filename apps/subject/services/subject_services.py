from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError

from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject


class SubjectService:
    @staticmethod
    @transaction.atomic
    def create_subject(*, course_id: int, data: dict[str, Any]) -> Subject:
        title_obj = data.get("title")

        if not isinstance(title_obj, str):
            raise ValidationError(detail="유효하지 않은 과목 생성 요청입니다.")

        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise NotFound(detail="해당 과정을 찾을 수 없습니다.")

        if Subject.objects.filter(course=course, title=title_obj).exists():
            raise ValidationError(detail="동일한 이름의 과목이 이미 존재합니다.")

        try:
            subject = Subject.objects.create(
                course=course,
                title=title_obj,
                number_of_days=data["number_of_days"],
                number_of_hours=data["number_of_hours"],
                thumbnail_img_url=data.get("thumbnail_img_url"),
            )
        except IntegrityError:
            raise ValidationError(detail="유효하지 않은 과목 생성 요청입니다.")

        return subject

    @staticmethod
    def list_subjects_by_course(*, course_id: int) -> QuerySet[Subject]:
        return Subject.objects.filter(course_id=course_id).order_by("id")

    @staticmethod
    def get_subject(*, subject_id: int) -> Subject:
        return get_object_or_404(
            Subject.objects.select_related("course"),
            id=subject_id,
        )

    @staticmethod
    def get_subject_scatter_queryset(*, subject_id: int) -> QuerySet[ExamSubmission]:
        subject = SubjectService.get_subject(subject_id=subject_id)

        return (
            ExamSubmission.objects.filter(deployment__exam__subject=subject)
            .exclude(started_at__isnull=True)
            .exclude(created_at__isnull=True)
            .order_by("id")
        )
