from typing import Any

from django.shortcuts import get_object_or_404

from apps.exam.models.exam_submission_models import ExamSubmission
from apps.users.models.models import User


class CohortStudentService:

    @staticmethod
    def get_student_scores(*, student_id: int) -> list[dict[str, Any]]:
        user = get_object_or_404(User, id=student_id)

        submissions = ExamSubmission.objects.filter(submitter=user).select_related("deployment__exam__subject")

        result: dict[str, list[int]] = {}

        for sub in submissions:
            subject = sub.deployment.exam.subject.title
            if subject not in result:
                result[subject] = []
            result[subject].append(sub.score)

        return [
            {
                "subject": subject,
                "score": int(sum(scores) / len(scores)),
            }
            for subject, scores in result.items()
        ]
