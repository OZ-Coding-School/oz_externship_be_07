from typing import Any

from rest_framework import serializers

from apps.exam.models.exam_deployment_models import ExamDeployment
from apps.exam.models.exam_models import Exam
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


# 쪽지시험 결과 확인
class ExamSubmissionResultSerializer(serializers.ModelSerializer[ExamSubmission]):
    id = serializers.IntegerField(source="id", read_only=True)
    submitter_id = serializers.IntegerField(source="submitter.id", read_only=True)
    deployment_id = serializers.IntegerField(source="deployment.id", read_only=True)
    exam = ExamItemSerializer()
    questions = serializers.SerializerMethodField()
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

    def get_questions(self, obj: ExamSubmission) -> list[dict[str, Any]]:
        snapshot = obj.deployment.questions_snapshot_json
        submitted_answers = obj.answers_json

        answer_map = {ans.get("question_id"): ans.get("submitted_answer") for ans in submitted_answers}

        questions = []

        for index, q_info in enumerate(snapshot, start=1):
            q_id = q_info.get("id")
            submitted_val = answer_map.get(q_id)
            correct_val = q_info.get("answer")

            questions.append(
                {
                    "id": q_id,
                    "question": q_info.get("question"),
                    "prompt": q_info.get("prompt", ""),
                    "blank_count": q_info.get("blank_count", 0),
                    "options": q_info.get("options", []),
                    "type": q_info.get("type", ""),
                    "answer": correct_val,
                    "point": q_info.get("point", 0),
                    "explanation": q_info.get("explanation", ""),
                    "is_correct": submitted_val == correct_val,
                    "submitted_answer": submitted_val,
                }
            )

        return questions


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
    questions = serializers.SerializerMethodField()

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

    def get_questions(self, obj: ExamSubmission) -> list[dict[str, Any]]:
        snapshot = obj.deployment.questions_snapshot_json
        submitted_answers = obj.answers_json

        answer_map = {ans.get("question_id"): ans.get("submitted_answer") for ans in submitted_answers}

        processed_questions = []

        for index, q_info in enumerate(snapshot, start=1):
            q_id = q_info.get("id")
            submitted_val = answer_map.get(q_id)
            correct_val = q_info.get("answer")

            processed_questions.append(
                {
                    "id": q_id,
                    "number": index,
                    "type": q_info.get("type"),
                    "question": q_info.get("question"),
                    "prompt": q_info.get("prompt", ""),
                    "options": q_info.get("options", []),
                    "point": q_info.get("point", 0),
                    "answer": correct_val,
                    "submitted_answer": submitted_val,
                    "is_correct": submitted_val == correct_val,
                    "explanation": q_info.get("explanation", ""),
                }
            )

        return processed_questions
