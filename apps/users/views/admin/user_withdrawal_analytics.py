from datetime import datetime, timedelta

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin.user_withdrawal_analytics import (
    WithdrawalMonthlyReasonStatsSerializer,
    WithdrawalReasonCountSerializer,
)
from apps.users.services.admin.user_withdrawal_analytics import (
    get_monthly_withdrawal_reason_stats_service,
    get_withdrawal_reason_counts_service,
)


class BaseWithdrawalAnalyticsAPIView(APIView):
    def get_dates(self, request: Request) -> tuple[datetime, datetime]:
        from_date_str = request.query_params.get("from_date")
        to_date_str = request.query_params.get("to_date")
        now = timezone.now()

        try:
            if from_date_str:
                naive_from = datetime.strptime(from_date_str, "%Y-%m-%d")
                from_date = timezone.make_aware(naive_from).replace(hour=0, minute=0, second=0)
            else:
                from_date = (now - timedelta(days=365)).replace(hour=0, minute=0, second=0)

            if to_date_str:
                naive_to = datetime.strptime(to_date_str, "%Y-%m-%d")
                to_date = timezone.make_aware(naive_to).replace(hour=23, minute=59, second=59)
            else:
                to_date = now.replace(hour=23, minute=59, second=59)

        except ValueError:
            raise ValidationError({"error": "날짜 형식이 올바르지 않습니다. (YYYY-MM-DD 권장)"})

        if from_date > to_date:
            raise ValidationError({"error": "시작일(from_date)은 종료일(to_date)보다 이전이어야 합니다."})

        return from_date, to_date


class WithdrawalReasonCountAPIView(BaseWithdrawalAnalyticsAPIView):
    @extend_schema(
        summary="탈퇴 사유별 갯수 분석",
        parameters=[
            OpenApiParameter("from_date", type=OpenApiTypes.DATE, description="시작일 (YYYY-MM-DD)"),
            OpenApiParameter("to_date", type=OpenApiTypes.DATE, description="종료일 (YYYY-MM-DD)"),
        ],
        responses={200: WithdrawalReasonCountSerializer},
        tags=["admin_accounts"],
    )
    def get(self, request: Request) -> Response:
        from_date, to_date = self.get_dates(request)
        data = get_withdrawal_reason_counts_service(from_date, to_date)

        serializer = WithdrawalReasonCountSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WithdrawalMonthlyReasonStatsAPIView(BaseWithdrawalAnalyticsAPIView):
    @extend_schema(
        summary="특정 사유의 월별 탈퇴 추세",
        parameters=[
            OpenApiParameter("reason", str, description="탈퇴 사유 코드", required=True),
            OpenApiParameter("from_date", type=OpenApiTypes.DATE, description="시작일 (YYYY-MM-DD)"),
            OpenApiParameter("to_date", type=OpenApiTypes.DATE, description="종료일 (YYYY-MM-DD)"),
        ],
        responses={200: WithdrawalMonthlyReasonStatsSerializer},
        tags=["admin_accounts"],
    )
    def get(self, request: Request) -> Response:
        reason = request.query_params.get("reason")

        if not reason:
            raise ValidationError({"reason": "필수 파라미터입니다."})

        from_date, to_date = self.get_dates(request)
        data = get_monthly_withdrawal_reason_stats_service(reason, from_date, to_date)

        serializer = WithdrawalMonthlyReasonStatsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
