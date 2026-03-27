import logging
from datetime import timedelta

from celery import shared_task  # type: ignore
from django.utils import timezone

from apps.chatbot.models import ChatbotSessions

logger = logging.getLogger(__name__)


@shared_task  # type:ignore[misc]
def delete_expired_chatbot_sessions() -> int:
    """
    [Celery Task] 생성된 지 1시간이 지난 QnA 챗봇 세션을 자동 삭제합니다.
    """

    time_threshold = timezone.now() - timedelta(hours=1)

    # 1시간 넘은 세션들 필터링
    expired_sessions = ChatbotSessions.objects.filter(updated_at__lt=time_threshold)
    count = expired_sessions.count()

    if count > 0:
        #  일괄 삭제 (Cascade 옵션, completions 도 같이 날라감)
        expired_sessions.delete()
        logger.info(f" [Celery] 1시간 경과 챗봇 세션 {count}개 정리 완료.")
    else:
        logger.info(" [Celery] 삭제할 만료 챗봇 세션이 없습니다.")

    return count
