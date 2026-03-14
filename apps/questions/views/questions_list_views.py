from typing import Any, List

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.views.questions_create_views import QuestionCreateView
from apps.questions.views.questions_update_views import QuestionUpdateView


# 1. 목록 조회(GET) 및 등록(POST) 통합 관리
class QuestionListView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(tags=["qna"], summary="질문 조회", description="질문조회 작성 API")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """질문 목록 조회 MOCK"""
        mock_data = {
            "count": 152,
            "next": "null",
            "previous": "null",
            "results": [
                {
                    "id": 10501,
                    "category": {"id": 12, "depth": 2, "names": ["백엔드", "Django", "ORM"]},
                    "author": {
                        "id": 211,
                        "nickname": "백엔드",
                        "profile_image_url": "https://cdn.ozcodingschool.com/profiles/user_123.png",
                    },
                    "title": "Django ORM 역참조는 어떻게 사용하나요?",
                    "content_preview": "ForeignKey에 related_name을 지정하면.....",
                    "answer_count": 3,
                    "view_count": 87,
                    "created_at": "2025-03-01 10:03:21",
                    "thumbnail_url": "https://cdn.ozcodingschool.com/qna/thumb_10501_01.png",
                }
            ],
        }

        error = {
            "400": {"error_detail": "유효하지 않은 목록 조회 요청입니다."},
            "404": {"error_detail": "조회 가능한 질문이 존재하지 않습니다."},
        }

        return Response(mock_data, status=status.HTTP_200_OK)
        # return Response(error["404"], status=status.HTTP_404_NOT_FOUND)

    @extend_schema(tags=["qna"], summary="질문 등록", description="질문등록 작성 API")
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """기존 QuestionCreateView의 post 로직 호출"""
        return QuestionCreateView().post(request, *args, **kwargs)


# 2. 상세 조회(GET) 및 수정(PUT) 통합 관리
class QuestionListDetailView(APIView):
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "PUT":
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(tags=["qna"], summary="질문 조회", description="질문 상세조회 작성 API")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """질문 상세 조회 MOCK"""
        mock_detail = {
            "id": 10501,
            "title": "Django에서 ForeignKey 역참조는 어떻게 하나요?",
            "content": "Django 모델에서 related_name을 지정했을 떄....",
            "category": {"id": 12, "depth": 3, "names": ["백엔드", "Django", "ORM"]},
            "images": [{"id": 3, "img_url": "https://cdn.ozcodingschool.com/qna/img_20250301_101530.png"}],
            "view_count": 88,
            "created_at": "2025-03-01 10:25:33",
            "author": {"id": 211, "nickname": "백엔드", "profile_image_url": "null"},
            "answers": [
                {
                    "id": 501,
                    "content": "related_name을 지정하면 역참조 시 해당 이름으로 접근할 수 있습니다. 예를들어'post.comments.all()' 형태로 사용합니다.",
                    "created_at": "2025-03-01 11:30:00",
                    "is_adopted": True,
                    "author": {
                        "id": 102,
                        "nickname": "김오즈",
                        "profile_image_url": "https://cdn.ozcodingschool.com/profile/user102.png",
                    },
                    "comments": [
                        {
                            "id": 1001,
                            "content": "답변 감사합니다! 덕분에 이해됐어요.",
                            "created_at": "2025-03-01 12:00:05",
                            "author": {"id": 211, "nickname": "백엔드", "profile_image_url": "null"},
                        },
                        {
                            "id": 1002,
                            "content": "추가로 prefetch_related도 같이 쓰시면 좋아요.",
                            "created_at": "2025-03-01 12:15:00",
                            "author": {
                                "id": 102,
                                "nickname": "김오즈",
                                "profile_image_url": "https://cdn.ozcodingschool.com/profile/user102.png",
                            },
                        },
                    ],
                },
                {
                    "id": 502,
                    "content": "select_related와 prefetch_related 차이도 알아두시면 좋습니다.",
                    "created_at": "2025-03-01 14:00:00",
                    "is_adopted": False,
                    "author": {"id": 305, "nickname": "심상보", "profile_image_url": "null"},
                    "comments": [],
                },
            ],
        }

        error = {
            "400": {"error_detail": "유효하지 않은 목록 조회 요청입니다."},
            "404": {"error_detail": "조회 가능한 질문이 존재하지 않습니다."},
        }

        return Response(mock_detail, status=status.HTTP_200_OK)
        # return Response(error["404"], status=status.HTTP_404_NOT_FOUND)

    @extend_schema(tags=["qna"], summary="질문 수정", description="질문 수정 API")
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """기존 QuestionUpdateView의 put 로직 호출"""
        return QuestionUpdateView().put(request, *args, **kwargs)
