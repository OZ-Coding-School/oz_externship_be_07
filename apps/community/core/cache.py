from django.core.cache import caches

cache = caches["hit_like"]


def cache_get_int(key: str, default: int = 0) -> int:
    value = cache.get(key)
    return int(value) if value is not None else default


def cache_add(key: str, value: int, timeout: int) -> bool:
    return bool(cache.add(key, value, timeout=timeout))


def cache_incr(key: str, delta: int = 1) -> int:
    try:
        return int(cache.incr(key, delta))
    except ValueError:
        cache.set(key, delta)
        return delta
