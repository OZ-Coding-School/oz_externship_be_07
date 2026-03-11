import string
import secrets
from django.db import transaction
from django.db.models import Avg, Count
from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_question_models import ExamQuestion


class ExamDeploymentService:
    @staticmethod
    def _generate_access_code(length=8):
        """중복되지 않는 액세스 코드 생성"""
        chars = string.digits + string.ascii_letters
        while True:
            code = "".join(secrets.choice(chars) for _ in range(length))
            if not ExamDeployment.objects.filter(access_code=code).exists():
                return code

    @staticmethod
    def _build_questions_snapshot(exam):
        """시험 질문의 현재 상태를 JSON 스냅샷으로 변환"""
        questions = ExamQuestion.objects.filter(exam=exam).order_by("id")
        return [
            {
                "id": q.id,
                "question": q.question,
                "prompt": q.prompt,
                "blank_count": q.blank_count,
                "options_json": q.options_json,
                "type": q.type,
                "answer": q.answer,
                "point": q.point,
                "explanation": q.explanation,
            }
            for q in questions
        ]

    @classmethod
    @transaction.atomic
    def create_deployment(cls, validated_data):
        """배포 생성 및 관련 정보 자동 생성"""
        exam = validated_data.get("exam")
        validated_data["access_code"] = cls._generate_access_code()
        validated_data["questions_snapshot_json"] = cls._build_questions_snapshot(exam)
        return ExamDeployment.objects.create(**validated_data)

    @staticmethod
    def get_deployment_list_queryset():
        """통계 정보를 포함한 배포 쿼리셋 반환"""
        return ExamDeployment.objects.select_related("exam", "exam__subject", "cohort", "cohort__course").annotate(
            submit_count=Count("examsubmission", distinct=True),
            avg_score=Avg("examsubmission__score"),
        )

    @staticmethod
    def get_total_student_count(cohort):
        """기수의 총 학생 수 계산"""
        for name in ["cohort_students", "cohortstudent_set", "students"]:
            relation = getattr(cohort, name, None)
            if relation is not None and hasattr(relation, "count"):
                return relation.count()
        return 0
