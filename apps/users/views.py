from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import SignUpSerializer


class SignUpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="회원가입 API",
        description="사용자 정보를 모든 필드를 필수로 입력받고 중복체크후 새로운 회원을 생성합니다.",
        request=SignUpSerializer,
        responses={
            201: {"description": "회원가입 성공", "example": {"detail": "회원가입이 완료되었습니다."}},
            400: {
                "description": "필수값 누락 또는 형식 오류",
                "example": {"error_detail": "모든 필드는 필수 항목입니다."},
            },
            409: {
                "description": "이메일 중복 오류",
                "example": {"error_detail": "이미 가입된 정보(이메일/핸드폰/닉네임)가 존재합니다."},
            },
        },
    )
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            return Response({"error_detail": "이미 가입된 이메일이 존재합니다."}, status=status.HTTP_409_CONFLICT)

        phone_number = request.data.get("phone_number")
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({"error_detail": "이미 가입된 핸드폰번호가 존재합니다."}, status=status.HTTP_409_CONFLICT)

        nickname = request.data.get("nickname")
        if User.objects.filter(nickname=nickname).exists():
            return Response({"error_detail": "이미 사용 중인 닉네임입니다."}, status=status.HTTP_409_CONFLICT)

        serializer.save()
        return Response({"detail": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
