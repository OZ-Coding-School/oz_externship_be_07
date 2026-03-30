from collections import defaultdict
from typing import Any

from django.http import Http404

from apps.exam.models.exam_submission_models import ExamSubmission
from apps.users.models.models import User


class CohortStudentService:
    STUDENT_NOT_FOUND_MESSAGE = "학생을 찾을 수 없습니다."

    @staticmethod
    def get_student_scores(*, student_id: int) -> list[dict[str, Any]]:
        try:
            user = User.objects.get(id=student_id)
        except User.DoesNotExist:
            raise Http404(CohortStudentService.STUDENT_NOT_FOUND_MESSAGE)

        submissions = (
            ExamSubmission.objects.filter(submitter=user).select_related("deployment__exam__subject").order_by("id")
        )

        scores_by_subject: dict[str, list[int]] = defaultdict(list)

        for submission in submissions:
            subject_title = submission.deployment.exam.subject.title
            scores_by_subject[subject_title].append(submission.score)

        return [
            {
                "subject": subject,
                "score": int(sum(scores) / len(scores)),
            }
            for subject, scores in scores_by_subject.items()
        ]
