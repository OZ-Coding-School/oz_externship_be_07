from typing import Any

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStaffUser
from apps.users.models.models import User, Withdrawal
from apps.users.serializers.admin.user_analytics import AdminAnalyticsTrendSerializer
from apps.users.services.admin.user_analytics import get_analytics_trend_service


class BaseAnalyticsTrendAPIView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
    model_class: Any = None

    def get(self, request: Request) -> Response:
        interval = request.query_params.get("interval", "monthly")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        data = get_analytics_trend_service(self.model_class, interval, from_date, to_date)
        serializer = AdminAnalyticsTrendSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="어드민 회원가입 추세 분석",
    parameters=[
        OpenApiParameter(name="interval", description="분석 간격 (monthly/yearly)", required=True, type=str),
        OpenApiParameter(name="from_date", description="시작일 (YYYY-MM-DD)", type=str),
        OpenApiParameter(name="to_date", description="종료일 (YYYY-MM-DD)", type=str),
    ],
    responses={
        200: AdminAnalyticsTrendSerializer,
        401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
    },
    tags=["admin_accounts"],
)
class AdminSignupTrendAPIView(BaseAnalyticsTrendAPIView):
    model_class = User


@extend_schema(
    summary="어드민 회원탈퇴 추세 분석",
    parameters=[
        OpenApiParameter(name="interval", description="분석 간격 (monthly/yearly)", required=True, type=str),
        OpenApiParameter(name="from_date", description="시작일 (YYYY-MM-DD)", type=str),
        OpenApiParameter(name="to_date", description="종료일 (YYYY-MM-DD)", type=str),
    ],
    responses={
        200: AdminAnalyticsTrendSerializer,
        401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
    },
    tags=["admin_accounts"],
)
class AdminWithdrawalTrendAPIView(BaseAnalyticsTrendAPIView):
    model_class = Withdrawal
