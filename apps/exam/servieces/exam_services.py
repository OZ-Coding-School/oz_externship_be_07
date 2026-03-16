from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator

from apps.exam.models.exam_models import Exam


class ExamService:
    @staticmethod
    def get_exam_list(page=1, size=10, search_keyword=None, subject_id=None, sort="created_at", order="desc"):
        """
        시험 목록 조회, 필터링, 정렬 및 페이지네이션
        """
        # 1. 초기 쿼리셋 (N+1 방지를 위해 select_related 추가)
        exams = Exam.objects.select_related('subject').all()

        # 2. 필터링 (과목 ID)
        if subject_id:
            exams = exams.filter(subject_id=subject_id)

        # 3. 필터링 (검색어)
        if search_keyword:
            exams = exams.filter(title__icontains=search_keyword)

        # 4. 정렬 처리
        # order가 'desc'이면 필드명 앞에 '-'를 붙임
        order_by = f"-{sort}" if order == "desc" else sort
        exams = exams.order_by(order_by)

        # 5. 페이지네이션
        paginator = Paginator(exams, size)
        page_obj = paginator.get_page(page)

        return page_obj

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
