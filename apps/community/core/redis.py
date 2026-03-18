import json
from typing import Any

from django_redis import get_redis_connection  # type: ignore
from redis import Redis


class RedisClient:
    @staticmethod
    def _get_index(name: str = "default") -> Any:
        """
        redis 연결
        """
        return get_redis_connection(name)

    @classmethod
    def set_string(cls, key: str, value: str, name: str = "default", timeout: int | None = None) -> bool:
        """
        string 저장
        """
        try:
            conn = cls._get_index(name)
            if timeout:
                return bool(conn.setex(key, timeout, value))
            return bool(conn.set(key, value))
        except Exception as e:
            print(f"string set Error: {e}")
            return False

    @classmethod
    def get_string(cls, key: str, name: str = "default") -> str | None:
        """
        string 조회
        """
        try:
            data = cls._get_index(name).get(key)
            return data.decode("utf-8") if data else None
        except Exception as e:
            print(f"string get Error: {e}")
            return None

    @classmethod
    def set_json(cls, key: str, value: Any, name: str = "default", timeout: int | None = None) -> bool:
        """
        딕셔너리,리스트 json으로 저장
        """
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            return cls.set_string(key, json_value, name, timeout)
        except (TypeError, ValueError) as e:
            print(f"json serialization Error: {e}")
            return False

    @classmethod
    def get_json(cls, key: str, name: str = "default") -> Any:
        """
        json decode 가져오기
        """
        data = cls.get_string(key, name)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                print(f"json decode Error: {e}")
                return None
        return None
