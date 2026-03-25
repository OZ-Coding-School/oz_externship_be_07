import json
from typing import Any

from django.db import models

from apps.exam.core.error_custom_base import ConflictException
from apps.exam.models.exam_models import Exam
from apps.exam.models.exam_question_models import ExamQuestion

MAX_QUESTION_COUNT = 10
MAX_TOTAL_POINT = 100
MAX_POINT_PER_QUESTION = 10


class ExamQuestionService:

    @staticmethod
    def create_question(exam: Exam, data: dict[str, Any]) -> ExamQuestion:

        current_count = ExamQuestion.objects.filter(exam=exam).count()
        if current_count >= MAX_QUESTION_COUNT:
            raise ConflictException("해당 쪽지시험에 등록 가능한 문제 수 또는 총 배점을 초과했습니다,")

        if data["point"] > MAX_POINT_PER_QUESTION:
            raise ConflictException("해당 쪽지시험에 등록 가능한 문제 수 또는 총 배점을 초과했습니다.")

        current_total = (
            ExamQuestion.objects.filter(exam=exam).aggregate(
                total=models.Sum("point", output_field=models.FloatField())
            )["total"]
            or 0
        )
        if current_total + data["point"] > MAX_TOTAL_POINT:
            raise ConflictException("해당 쪽지시험에 등록 가능한 문제 수 또는 총 배점을 초과했습니다.")

        options_json: str | None
        if data.get("options") is not None:
            options_json = json.dumps(data["options"], ensure_ascii=False)

        return ExamQuestion.objects.create(
            exam=exam,
            type=data["type"],
            question=data["question"],
            prompt=data.get("prompt"),
            options_json=options_json,
            blank_count=data.get("blank_count"),
            answer=data["correct_answer"],
            point=data["point"],
            explanation=data["explanation"],
        )

    @staticmethod
    def update_question(question: ExamQuestion, data: dict[str, Any]) -> ExamQuestion:

        if "point" in data:
            if data["point"] > MAX_POINT_PER_QUESTION:
                raise ConflictException("시험 문제 수 제한 또는 총 배점을 초과하여 문제를 수정할 수 없습니다.")

        current_total = (
            ExamQuestion.objects.filter(exam=question.exam)
            .exclude(id=question.id)
            .aggregate(total=models.Sum("point", output_field=models.FloatField()))["total"]
            or 0
        )
        if current_total + data["point"] > MAX_TOTAL_POINT:
            raise ConflictException("시험 문제 수 제한 또는 총 배점을 초과하여 문제를 수정할 수 없습니다.")

        if "options" in data:
            question.options_json = (
                json.dumps(data["options"], ensure_ascii=False) if data["options"] is not None else None
            )
        if "type" in data:
            question.type = data["type"]
        if "question" in data:
            question.question = data["question"]
        if "prompt" in data:
            question.prompt = data["prompt"]
        if "blank_count" in data:
            question.blank_count = data["blank_count"]
        if "correct_answer" in data:
            question.answer = data["correct_answer"]
        if "point" in data:
            question.point = data["point"]
        if "explanation" in data:
            question.explanation = data["explanation"]

        question.save()
        return question

    @staticmethod
    def delete_question(question: ExamQuestion) -> dict[str, Any]:

        exam_id: int = question.exam_id
        question_id: int = question.id
        question.delete()
        return {"exam_id": exam_id, "question_id": question_id}
