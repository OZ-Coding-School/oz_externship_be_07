from typing import Any, Dict, List

from django.test import TestCase
from django_redis import get_redis_connection  # type: ignore
from rest_framework.test import APIRequestFactory

from apps.community.serializers.comment_serializers import (
    PostCommentUserSearchSerializer,
)


class UserLogicTest(TestCase):
    test_entry: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.test_entry = "apple:1:https://example.com/img.png"

        conn = get_redis_connection("default")
        conn.execute_command("ZADD", "default", 0, cls.test_entry)

    @property
    def factory(self) -> APIRequestFactory:
        return APIRequestFactory()

    @property
    def redis_conn(self) -> Any:
        return get_redis_connection("default")

    def tearDown(self) -> None:
        self.redis_conn.execute_command("ZREM", "default", self.test_entry)

    def test_logic_step_by_step(self) -> None:
        search_query = "app"
        list_results = self.redis_conn.execute_command(
            "ZRANGEBYLEX", "default", f"[{search_query}", f"[{search_query}\xff"
        )
        results: List[Dict[str, Any]] = []
        for encoded_byte in list_results:
            decoded_byte = encoded_byte.decode("utf-8")
            parts = decoded_byte.split(":", 2)
            if len(parts) == 3:
                results.append({"id": int(parts[1]), "nickname": parts[0], "profile_img_url": parts[2]})

        serializer = PostCommentUserSearchSerializer(results, many=True)

        self.assertEqual(len(serializer.data), 1)
        self.assertEqual(serializer.data[0]["nickname"], "apple")
