from typing import List, Optional

from diskcache import Cache

from .config import config


def upsert_cache(cache: Cache, name: str, result: List[str]) -> None:
    cache.set(name, result, expire=config.cache_expire * 24 * 60 * 60)


def exist_in_cache(cache: Cache, name: str) -> Optional[List[str]]:
    cache_result: Optional[List[str]] = cache.get(name)
    if cache_result:
        cache.touch(name, expire=config.cache_expire * 24 * 60 * 60)
    return cache_result
