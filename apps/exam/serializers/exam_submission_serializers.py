from typing import Any

from django.utils import timezone
from rest_framework import serializers

from apps.exam.models.exam_submission_models import ExamSubmission


class ExamSubmissionListSerializer(serializers.ModelSerializer[ExamSubmission]):
    """목록 조회용: 간단한 요약 정보 반환"""

    submission = serializers.IntegerField(source="id")
    student_name = serializers.CharField(source="submitter.name", read_only=True)
    course_name = serializers.CharField(
        source="deployment.cohort.course.name",
        default="N/A",
    )
    cohort_number = serializers.IntegerField(source="deployment.cohort.number", read_only=True)
    exam_title = serializers.CharField(source="deployment.exam.title", read_only=True)
    subject_name = serializers.CharField(source="deployment.exam.subject.title", read_only=True)
    finished_at = serializers.DateTimeField(source="created_at")

    class Meta:
        model = ExamSubmission
        fields = [
            "submission",
            "student_name",
            "course_name",
            "cohort_number",
            "exam_title",
            "subject_name",
            "cheating_count",
            "started_at",
            "finished_at",
        ]


class ExamSubmissionDetailSerializer(serializers.ModelSerializer[ExamSubmission]):
    """상세 조회용: 명세서의 중첩 구조(Nested) 구현"""

    exam = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    questions = serializers.JSONField(source="answers_json")

    class Meta:
        model = ExamSubmission
        fields = ["exam", "student", "result", "questions"]

    def get_exam(self, obj: ExamSubmission) -> dict[str, Any]:
        deployment = obj.deployment
        return {
            "exam_title": deployment.exam.title,
            "subject_name": deployment.exam.subject.title,
            "duration_time": deployment.duration_time,
            "open_at": deployment.open_at,
            "close_at": deployment.close_at,
        }

    def get_student(self, obj: ExamSubmission) -> dict[str, Any]:
        user = obj.submitter
        return {
            "nickname": getattr(user, "nickname", user.username),
            "name": user.name if hasattr(user, "name") else user.username,
            "course_name": obj.deployment.cohort.course.name,
            "cohort_number": obj.deployment.cohort.number,
        }

    def get_result(self, obj: ExamSubmission) -> dict[str, Any]:
        elapsed_seconds = (obj.created_at - obj.started_at).total_seconds()

        return {
            "score": obj.score,
            "correct_answer_count": obj.correct_answer_count,
            "total_question_count": 10,
            "cheating_count": obj.cheating_count,
            "elapsed_time": int(elapsed_seconds // 60) if elapsed_seconds > 0 else 0,
        }