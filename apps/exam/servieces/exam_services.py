from typing import Any
from django.db.models import QuerySet
from django.core.paginator import Paginator, Page
from apps.exam.models.exam_models import Exam

class ExamService:
    @staticmethod
    def get_exam_list(
        page: int = 1,
        size: int = 10,
        search_keyword: str | None = None,
        subject_id: str | None = None,
        sort: str = "created_at",
        order: str = "desc"
    ) -> Page[Exam]:
        """시험 목록 조회 (Paginator의 Page 객체 반환)"""
        exams = Exam.objects.select_related('subject').all()

        if subject_id:
            exams = exams.filter(subject_id=subject_id)

        if search_keyword:
            exams = exams.filter(title__icontains=search_keyword)

        order_by = f"-{sort}" if order == "desc" else sort
        exams = exams.order_by(order_by)

        paginator = Paginator(exams, size)
        return paginator.get_page(page)

    @staticmethod
    def create_exam(validated_data: dict[str, Any]) -> Exam:
        """시험 생성"""
        thumbnail_img = validated_data.pop("thumbnail_img", None)
        if thumbnail_img:
            validated_data["thumbnail_img_url"] = (
                f"https://oz-externship.s3.ap-northeast-2.amazonaws.com/exams/{thumbnail_img.name}"
            )
        return Exam.objects.create(**validated_data)

    @staticmethod
    def update_exam(exam_id: int, validated_data: dict[str, Any]) -> Exam:
        """시험 정보 수정"""
        exam = Exam.objects.get(id=exam_id)
        thumbnail_img = validated_data.pop("thumbnail_img", None)

        if thumbnail_img:
            exam.thumbnail_img_url = f"https://oz-externship.s3.ap-northeast-2.amazonaws.com/exams/{thumbnail_img.name}"

        for attr, value in validated_data.items():
            setattr(exam, attr, value)

        exam.save()
        return exam

    @staticmethod
    def delete_exam(exam_id: int) -> int:
        """시험 삭제"""
        exam = Exam.objects.get(id=exam_id)
        exam.delete()
        return exam_id