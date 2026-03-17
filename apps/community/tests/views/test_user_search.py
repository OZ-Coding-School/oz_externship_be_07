import json

from django.test import TestCase
from django_redis import get_redis_connection  # type: ignore
from rest_framework.test import APIRequestFactory

from apps.community.serializers.comment_serializers import (
    PostCommentUserSearchSerializer,
)


class UserLogicTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.factory = APIRequestFactory()
        cls.redis_conn = get_redis_connection("default")

        cls.test_entry = "apple:1:https://example.com/img.png"
        cls.redis_conn.execute_command("ZADD", "default", 0, cls.test_entry)

        print("\n" + "-----------------------------------")
        print("view logic test")
        print("----------------------------------")

    def tearDown(self) -> None:
        self.redis_conn.execute_command("ZREM", "default", self.test_entry)

    def test_logic_step_by_step(self) -> None:
        search_query = "app"
        list_results = self.redis_conn.execute_command(
            "ZRANGEBYLEX", "default", f"[{search_query}", f"[{search_query}\xff"
        )
        print(f"\n1. byte data: {list_results}")

        results = []
        for encoded_byte in list_results:
            decoded_byte = encoded_byte.decode("utf-8")
            parts = decoded_byte.split(":", 2)
            if len(parts) == 3:
                results.append({"id": int(parts[1]), "nickname": parts[0], "profile_img_url": parts[2]})
        print(f"2. decode data: {results}")

        print("3. serializer 변환:")
        serializer = PostCommentUserSearchSerializer(results, many=True)

        print(json.dumps(serializer.data, indent=2, ensure_ascii=False))

        self.assertEqual(len(serializer.data), 1)
        self.assertEqual(serializer.data[0]["nickname"], "apple")
        print("\n성공")
