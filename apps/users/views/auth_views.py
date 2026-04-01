from django.conf import settings
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers.login_serializers import LoginSerializer
from apps.users.serializers.signup_serializers import SignUpSerializer
from apps.users.services.auth_services import (
    DuplicateUserError,
    LoginService,
    ReTokenService,
    SignUpService,
)


class SignUpView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SignUpSerializer

    @extend_schema(
        summary="회원가입",
        description="사용자 정보를 입력받아 계정을 생성하고 가입 정보를 반환하는 API",
        tags=["Accounts"],
        examples=[
            OpenApiExample(
                name="회원가입 성공 예시",
                value={
                    "detail": "회원가입이 완료되었습니다.",
                    "user_info": {
                        "email": "test@example.com",
                        "nickname": "테스트유저",
                        "name": "홍길동",
                        "birthday": "1995-01-01",
                        "gender": "M",
                        "phone_number": "01012345678",
                    },
                },
                response_only=True,
                status_codes=["201"],
            )
        ],
        responses={
            201: SignUpSerializer,
            400: OpenApiResponse(description="요청 데이터 오류 (필수필드 누락)"),
            409: OpenApiResponse(description="이미 중복된 회원가입 내역이 존재합니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SignUpSerializer(data=request.data)

        # 이메일,핸드폰,닉네임 중복 검사
        if not serializer.is_valid():

            status_code: int = status.HTTP_400_BAD_REQUEST

            for field_errors in serializer.errors.values():
                for error in field_errors:
                    if error.code == "unique":
                        status_code = status.HTTP_409_CONFLICT
                        break

                if status_code == status.HTTP_409_CONFLICT:
                    break

            return Response({"error_detail": serializer.errors}, status=status_code)

        # 통과 후 생성
        try:
            user_service = SignUpService()
            user_service.create_user(serializer.validated_data)
            return Response({"detail": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)

        except DuplicateUserError:
            return Response(
                {"error_detail": "이미 중복된 회원가입 내역이 존재합니다."}, status=status.HTTP_409_CONFLICT
            )

        except ValidationError as e:
            return Response({"error_detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="로그인 API",
        tags=["Accounts"],
        description="이메일과 비밀번호로 로그인하고, access_token은 바디로, refresh_token은 쿠키로 받습니다.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="로그인 성공",
                response={
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string", "description": "서비스 이용을 위한 액세스 토큰"},
                    },
                },
            ),
            400: OpenApiResponse(description="잘못된 요청 (이메일/비밀번호 불일치)"),
            403: OpenApiResponse(description="탈퇴 신청 계정 (접근 권한 없음)"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = LoginService()
        try:
            result = service.login_user(serializer.validated_data)

            refresh_token = result.pop("refresh")
            response = Response(result, status=status.HTTP_200_OK)

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,
                domain=settings.COOKIE_DOMAIN,
                path="/",
            )
            return response

        except ValidationError as e:
            error_data = e.detail
            status_code: int = status.HTTP_400_BAD_REQUEST

            if isinstance(error_data, dict) and error_data.get("error_type") == "WITHDRAWN":
                status_code = status.HTTP_403_FORBIDDEN

            return Response(error_data, status=status_code)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="로그아웃 API",
        tags=["Accounts"],
        description="브라우저 쿠키에 저장된 refresh_token을 삭제해 로그아웃 처리합니다.",
        responses={
            200: OpenApiResponse(
                description="로그아웃 성공",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string", "description": "로그아웃 되었습니다."},
                    },
                },
            ),
            401: OpenApiResponse(description="인증 실패 (로그인 필요)"),
        },
    )
    def post(self, request: Request) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)  # type: ignore
                token.blacklist()
            except TokenError:
                pass

        response = Response(
            {"detail": "성공적으로 로그아웃 되었습니다."},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(key="refresh_token", path="/", samesite="Lax", domain=settings.COOKIE_DOMAIN)

        return response


class ReTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="JWT 토큰 재발급 API",
        tags=["Accounts"],
        description="쿠키의 refresh_token으로 access_token을 재발급합니다.",
        responses={
            200: OpenApiResponse(
                description="재발급 성공",
                response={
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string", "description": "서비스 이용을 위한 액세스 토큰"},
                    },
                },
            ),
            400: OpenApiResponse(description="error_detail: { refresh_token: [필수 항목 누락] }"),
            403: OpenApiResponse(description="error_detail: { detail: 로그인 세션 만료 }"),
        },
    )
    def post(self, request: Request) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error_detail": {"refresh_token": ["이 필드는 필수 항목입니다."]}}, status=status.HTTP_400_BAD_REQUEST
            )

        service = ReTokenService()
        try:
            access_token = service.refresh_access_token(refresh_token)
            return Response({"access_token": access_token}, status=status.HTTP_200_OK)

        except TokenError:
            return Response(
                {"error_detail": {"detail": "로그인 세션이 만료되었습니다."}}, status=status.HTTP_403_FORBIDDEN
            )
