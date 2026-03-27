from typing import Any

from apps.community.core.redis import RedisClient


class UserSearchService:
    @staticmethod
    def search_users(nickname: str) -> list[dict[str, Any]]:
        if not nickname.strip():
            return []

        redis_conn = RedisClient.get_index(name="user_search")

        start = f"[{nickname}".encode("utf-8")
        next_char = chr(ord(nickname[-1]) + 1)
        end_str = nickname[:-1] + next_char
        end = f"({end_str}".encode("utf-8")

        list_results = redis_conn.execute_command("ZRANGEBYLEX", "user_search", start, end)

        results = []
        for encoded_byte in list_results:
            decoded_str = encoded_byte.decode("utf-8")

            try:
                parts = decoded_str.split(":", 2)
                if len(parts) == 3:
                    nickname, user_id, profile_img_url = parts
                    results.append({"id": int(user_id), "nickname": nickname, "profile_img_url": profile_img_url})
            except ValueError:
                continue

        return results
