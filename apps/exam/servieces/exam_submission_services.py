from django.shortcuts import get_object_or_404

from apps.exam.models.exam_submission_models import ExamSubmission


class ExamSubmissionService:
    @staticmethod
    def get_submission_list(search_keyword=None):
        """응시 내역 조회 및 검색"""
        queryset = ExamSubmission.objects.all().select_related(
            "submitter", "deployment__exam__subject", "deployment__cohort"
        )
        if search_keyword:
            queryset = queryset.filter(submitter__name__icontains=search_keyword)
        return queryset

    @staticmethod
    def delete_submission(submission_id):
        """응시 내역 삭제"""
        submission = get_object_or_404(ExamSubmission, id=submission_id)
        submission.delete()
        return submission_id
