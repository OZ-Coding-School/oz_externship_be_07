from __future__ import annotations

from typing import cast

from django.test import SimpleTestCase
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from apps.subject.views.cohort_views import (
    check_admin_role,
    check_authenticated,
    error_response,
)


class CohortViewHelpersTests(SimpleTestCase):
    factory: APIRequestFactory

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_error_response_returns_correct_format(self) -> None:
        response = error_response(message="에러 발생", http_status=400)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error_detail": "에러 발생"})

    def test_check_authenticated_returns_response_when_not_authenticated(self) -> None:
        request = Request(self.factory.get("/test"))

        response = check_authenticated(request)

        self.assertIsNotNone(response)
        response = cast(Response, response)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})

    def test_check_authenticated_returns_none_when_authenticated(self) -> None:
        request = Request(self.factory.get("/test"))
        request.user = type("User", (), {"is_authenticated": True})()

        response = check_authenticated(request)

        self.assertIsNone(response)

    def test_check_admin_role_returns_403_when_not_admin(self) -> None:
        request = Request(self.factory.get("/test"))
        request.user = type("User", (), {"is_authenticated": True, "role": "USER"})()

        response = check_admin_role(request)

        self.assertIsNotNone(response)
        response = cast(Response, response)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {"error_detail": "권한이 없습니다."})

    def test_check_admin_role_returns_none_when_admin(self) -> None:
        request = Request(self.factory.get("/test"))
        request.user = type("User", (), {"is_authenticated": True, "role": "ADMIN"})()

        response = check_admin_role(request)

        self.assertIsNone(response)