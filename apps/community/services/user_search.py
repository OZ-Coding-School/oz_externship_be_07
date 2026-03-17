from typing import Any, Dict, List

from django_redis import get_redis_connection


class UserSearchService:
    @staticmethod
    def search_users(nickname: str) -> List[Dict[str, Any]]:
        if not nickname:
            return []

        redis_conn = get_redis_connection("user_search")

        list_results = redis_conn.execute_command("ZRANGEBYLEX", "user_search", f"[{nickname}", f"[{nickname}\xff")

        results = []
        for encoded_byte in list_results:
            decoded_byte = encoded_byte.decode("utf-8")

            try:
                parts = decoded_byte.split(":", 2)
                if len(parts) == 3:
                    nickname, user_id, profile_img_url = parts
                    results.append({"id": int(user_id), "nickname": nickname, "profile_img_url": profile_img_url})
            except ValueError:
                continue

        return results
