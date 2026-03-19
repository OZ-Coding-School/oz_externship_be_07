from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.services.social_login_services import (
    KakaoLoginService,
    NaverLoginService,
)


class KakaoLoginView(APIView):
    @extend_schema(
        summary="카카오 로그인/회원가입",
        tags=["Accounts"],
        description=""  ### ⚠️ 테스트 방법\n"
        "1. [이 링크](https://kauth.kakao.com/oauth/authorize?client_id=46f2c8d82f2e5fba81a1668b8d69380a&redirect_uri=http://localhost:8000/api/v1/accounts/social-login/kakao/callback&response_type=code)를 클릭해 로그인을 진행하세요.\n"
        "2. 리다이렉트된 주소창의 `code=` 뒷부분을 복사해서 아래 `code` 파라미터에 넣고 실행하세요.",
        parameters=[OpenApiParameter("code", str, description="카카오 인가 코드")],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                    "refresh_token": {"type": "string"},
                    "is_created": {"type": "boolean"},
                },
            }
        },
    )
    def get(self, request):
        code = request.query_params.get("code")
        service = KakaoLoginService()

        access_token = service.get_access_token(code)
        user_info = service.get_user_info(access_token)

        user_data = service.extract_user_data(user_info)

        login_data = service.get_or_create_user(user_data)

        return Response(login_data, status=status.HTTP_200_OK)


class NaverLoginView(APIView):
    @extend_schema(
        summary="네이버 로그인/회원가입",
        tags=["Accounts"],
        description=""  ### 🟢 네이버 테스트 방법\n"
        "1. **[네이버 로그인 링크](https://nid.naver.com/oauth2.0/authorize?client_id=PEuQXllXAuldamlc40oS&redirect_uri=http://localhost:8000/api/v1/accounts/social-login/naver/callback&response_type=code&state=RANDOM_STATE)** 를 클릭하세요.\n"
        "2. 네이버 로그인 후 주소창에 뜨는 `code=...` 뒷부분을 복사하세요.\n"
        "3. 아래 `code` 파라미터에 붙여넣고, `state` 파라미터에는 `RANDOM_STATE`를 입력하고 실행하세요.",
        parameters=[OpenApiParameter("code", str, description="네이버 인가 코드")],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                    "refresh_token": {"type": "string"},
                    "is_created": {"type": "boolean"},
                },
            }
        },
    )
    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        service = NaverLoginService()

        access_token = service.get_access_token(code, state)
        user_info = service.get_user_info(access_token)

        user_data = service.extract_user_data(user_info)

        login_data = service.get_or_create_user(user_data)

        return Response(login_data, status=status.HTTP_200_OK)
