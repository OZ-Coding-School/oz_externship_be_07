from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError

from apps.exam.models.exam_submission_models import ExamSubmission
from apps.subject.models.course_models import Course
from apps.subject.models.subject_models import Subject


class SubjectService:
    @staticmethod
    @transaction.atomic
    def create_subject(*, data: dict) -> Subject:
        course_id = data.get("course_id")
        title = data.get("title")

        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise NotFound(detail="해당 과정을 찾을 수 없습니다.")

        if Subject.objects.filter(course=course, title=title).exists():
            raise ValidationError(detail="동일한 이름의 과목이 이미 존재합니다.")

        try:
            subject = Subject.objects.create(
                course=course,
                title=title,
                number_of_days=data["number_of_days"],
                number_of_hours=data["number_of_hours"],
                thumbnail_img_url=data.get("thumbnail_img_url"),
            )
        except IntegrityError:
            raise ValidationError(detail="유효하지 않은 과목 생성 요청입니다.")

        return subject

    @staticmethod
    def list_subjects_by_course(*, course_id: int):
        return Subject.objects.filter(course_id=course_id).order_by("id")

    @staticmethod
    def get_subject(*, subject_id: int) -> Subject:
        return get_object_or_404(
            Subject.objects.select_related("course"),
            id=subject_id,
        )

    @staticmethod
    @transaction.atomic
    def update_subject(*, subject_id: int, data: dict) -> Subject:
        subject = SubjectService.get_subject(subject_id=subject_id)

        new_title = data.get("title")
        if new_title and new_title != subject.title:
            duplicated = (
                Subject.objects.filter(
                    course=subject.course,
                    title=new_title,
                )
                .exclude(id=subject.id)
                .exists()
            )
            if duplicated:
                raise ValidationError(detail="동일한 이름의 과목이 이미 존재합니다.")
            subject.title = new_title

        if "number_of_days" in data:
            subject.number_of_days = data["number_of_days"]

        if "number_of_hours" in data:
            subject.number_of_hours = data["number_of_hours"]

        if "thumbnail_img_url" in data:
            subject.thumbnail_img_url = data["thumbnail_img_url"]

        if "status" in data:
            subject.status = data["status"]

        try:
            subject.save()
        except IntegrityError:
            raise ValidationError(detail="유효하지 않은 과목 수정 요청입니다.")

        return subject

    @staticmethod
    @transaction.atomic
    def delete_subject(*, subject_id: int) -> None:
        subject = SubjectService.get_subject(subject_id=subject_id)
        subject.delete()

    @staticmethod
    def get_subject_scatter_queryset(subject_id: int):
        subject = SubjectService.get_subject(subject_id)

        return (
            ExamSubmission.objects.filter(exam__subject=subject)
            .exclude(started_at__isnull=True)
            .exclude(created_at__isnull=True)
            .order_by("id")
        )
