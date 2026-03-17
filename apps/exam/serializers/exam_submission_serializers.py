from typing import Any

from rest_framework import serializers

from apps.exam.models.exam_submission_models import ExamSubmission


class AnswerItemSerializer(serializers.Serializer[dict[str, Any]]):
    question_id = serializers.IntegerField()
    submitted_answer = serializers.JSONField()


class ExamSubmissionCreateSerializer(serializers.ModelSerializer[ExamSubmission]):
    answers_json = AnswerItemSerializer(many=True)

    class Meta:
        model = ExamSubmission
        fields = [
            "deployment",
            "started_at",
            "cheating_count",
            "answers_json",
        ]

    def create(self, validated_data: dict[str, Any]) -> ExamSubmission:
        return super().create(validated_data)


class ExamSubmissionListSerializer(serializers.ModelSerializer[ExamSubmission]):

    submission_id = serializers.IntegerField(source="id")
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
            "submission_id",
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
        name = (user.name if hasattr(user, "name") else "Unknown",)
        return {
            "nickname": getattr(user, "nickname", user.email),
            "name": name,
            "course_name": obj.deployment.cohort.course.name,
            "cohort_number": obj.deployment.cohort.number,
        }

    def get_result(self, obj: ExamSubmission) -> dict[str, Any]:
        # 소요 시간 계산
        elapsed_delta = obj.created_at - obj.started_at
        elapsed_time = int(elapsed_delta.total_seconds() // 60)

        total_questions = len(obj.deployment.questions_snapshot_json) if obj.deployment.questions_snapshot_json else 0

        return {
            "score": obj.score,
            "correct_answer_count": obj.correct_answer_count,
            "total_question_count": total_questions,
            "cheating_count": obj.cheating_count,
            "elapsed_time": max(0, elapsed_time),
        }
