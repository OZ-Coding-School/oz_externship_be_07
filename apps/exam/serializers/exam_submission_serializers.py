from typing import Any

from rest_framework import serializers

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion
from apps.exam.models.exam_submission_models import ExamSubmission


# 쪽지시험 제출 - answers
class AnswerItemSerializer(serializers.Serializer[dict[str, Any]]):
    question_id = serializers.IntegerField()
    type = serializers.CharField()
    submitted_answer = serializers.JSONField()


# 쪽지시험 제출
class ExamSubmissionCreateSerializer(serializers.ModelSerializer[ExamSubmission]):
    answers = AnswerItemSerializer(many=True, source="answers_json")
    deployment_id = serializers.IntegerField(source="deployment.id")

    class Meta:
        model = ExamSubmission
        fields = [
            "deployment_id",
            "started_at",
            "cheating_count",
            "answers",
        ]


# 쪽지시험 결과 확인 - exam
class ExamItemSerializer(serializers.ModelSerializer[Exam]):
    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "thumbnail_img_url",
        ]


# 쪽지시험 결과 확인 - question
class ExamQuestionItemSerializer(serializers.ModelSerializer[ExamQuestion]):
    number = serializers.IntegerField()
    options = serializers.IntegerField(source="options_json")
    is_correct = serializers.BooleanField()
    submitted_answer = serializers.JSONField()

    class Meta:
        model = ExamQuestion
        fields = [
            "id",
            "number",
            "question",
            "prompt",
            "blank_count",
            "options",
            "type",
            "answer",
            "point",
            "explanation",
            "is_correct",
            "submitted_answer",
        ]


# 쪽지시험 결과 확인
class ExamSubmissionResultSerializer(serializers.ModelSerializer[ExamSubmission]):
    id = serializers.IntegerField(source="id", read_only=True)
    submission_id = serializers.IntegerField(source="submitter.id", read_only=True)
    deployment_id = serializers.IntegerField(source="deployment.id", read_only=True)
    exam = ExamItemSerializer()
    questions = ExamQuestionItemSerializer()
    total_score = serializers.IntegerField(source="score", read_only=True)
    elapsed_time = serializers.SerializerMethodField()
    submitted_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = ExamSubmission
        fields = [
            "id",
            "submitter_id",
            "deployment_id",
            "exam",
            "questions",
            "cheating_count",
            "total_score",
            "correct_answer_count",
            "elapsed_time",
            "started_at",
            "submitted_at",
        ]

    def get_elapsed_time(self, obj: ExamSubmission) -> int:
        elapsed_delta = obj.created_at - obj.started_at
        elapsed_time = int(elapsed_delta.total_seconds() // 60)
        return max(0, elapsed_time)


# 쪽지시험 응시 내역 목록 조회 API
class ExamSubmissionListSerializer(serializers.ModelSerializer[ExamSubmission]):
    submission_id = serializers.IntegerField(source="id", read_only=True)
    nickname = serializers.CharField(source="submitter.nickname", read_only=True)
    name = serializers.CharField(source="submitter.name", read_only=True)
    course_name = serializers.CharField(source="deployment.cohort.course.name", read_only=True)
    cohort_number = serializers.IntegerField(source="deployment.cohort.number", read_only=True)
    exam_title = serializers.CharField(source="deployment.exam.title", read_only=True)
    subject_name = serializers.CharField(source="deployment.exam.subject.title", read_only=True)
    finished_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = ExamSubmission
        fields = [
            "submission_id",
            "nickname",
            "name",
            "course_name",
            "cohort_number",
            "exam_title",
            "subject_name",
            "score",
            "cheating_count",
            "started_at",
            "finished_at",
        ]


# 쪽지시험 응시 내역 상세 조회 API - exam
class ExamDeploymentItemSerializer(serializers.ModelSerializer[ExamDeployment]):
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    subject_name = serializers.CharField(source="exam.subject.title", read_only=True)

    class Meta:
        model = ExamDeployment
        fields = [
            "exam_title",
            "subject_name",
            "duration_time",
            "open_at",
            "close_at",
        ]


# 쪽지시험 응시 내역 상세 조회 API
class ExamSubmissionDetailSerializer(serializers.ModelSerializer[ExamSubmission]):
    exam = ExamDeploymentItemSerializer()
    student = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    questions = ExamQuestionItemSerializer()

    class Meta:
        model = ExamSubmission
        fields = ["exam", "student", "result", "questions"]

    def get_student(self, obj: ExamSubmission) -> dict[str, Any]:
        return {
            "nickname": obj.submitter.nickname,
            "name": obj.submitter.name,
            "course_name": obj.deployment.cohort.course.name,
            "cohort_number": obj.deployment.cohort.number,
        }

    def get_result(self, obj: ExamSubmission) -> dict[str, Any]:
        elapsed_delta = obj.created_at - obj.started_at
        elapsed_time = int(elapsed_delta.total_seconds() // 60)

        snapshot = obj.deployment.questions_snapshot_json
        total_questions = len(snapshot) if isinstance(snapshot, list) else 0

        return {
            "score": obj.score,
            "correct_answer_count": obj.correct_answer_count,
            "total_question_count": total_questions,
            "cheating_count": obj.cheating_count,
            "elapsed_time": max(0, elapsed_time),
        }
