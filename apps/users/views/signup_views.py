from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.signup_serializers import SignUpSerializer
from apps.users.services.signup_services import UserService


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
            user_service = UserService()
            user_service.create_user(serializer.validated_data)
            return Response({"detail": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)

        # 중복 가입 에러 처리
        except Exception:
            return Response(
                {"error_detail": "이미 중복된 회원가입 내역이 존재합니다."}, status=status.HTTP_409_CONFLICT
            )
