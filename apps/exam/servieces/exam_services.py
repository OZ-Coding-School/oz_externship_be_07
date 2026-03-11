from django.db import transaction

from apps.exam.models.exam_models import Exam


class ExamService:
    @staticmethod
    def get_exam_list(subject_id=None, search_keyword=None):
        """시험 목록 조회 및 필터링"""
        exams = Exam.objects.all().order_by("-created_at")
        if subject_id:
            exams = exams.filter(subject_id=subject_id)
        if search_keyword:
            exams = exams.filter(title__icontains=search_keyword)
        return exams

    @staticmethod
    def create_exam(validated_data):
        """시험 생성 로직"""
        thumbnail_img = validated_data.pop("thumbnail_img", None)
        if thumbnail_img:
            # S3 업로드 경로 설정
            validated_data["thumbnail_img_url"] = (
                f"https://oz-externship.s3.ap-northeast-2.amazonaws.com/exams/{thumbnail_img.name}"
            )
        return Exam.objects.create(**validated_data)

    @staticmethod
    def update_exam(exam_id, validated_data):
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
    def delete_exam(exam_id):
        """시험 삭제"""
        exam = Exam.objects.get(id=exam_id)
        exam.delete()
        return exam_id
