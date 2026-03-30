import json
from typing import Optional, Any
import redis
from app.core.config import settings


class CacheService:
    """Сервис для работы с Redis кэшем"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5
        )

    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Сохранить значение в кэш"""
        try:
            self.redis_client.setex(key, expire, json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Удалить из кэша"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Удалить все ключи по шаблону"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
        return 0

    # Специфичные методы
    def cache_listing(self, listing_id: int, data: dict, expire: int = 3600) -> bool:
        """Кэшировать объявление"""
        return self.set(f"listing:{listing_id}", data, expire)

    def get_cached_listing(self, listing_id: int) -> Optional[dict]:
        """Получить кэшированное объявление"""
        return self.get(f"listing:{listing_id}")

    def cache_search_results(self, query: str, data: list, expire: int = 300) -> bool:
        """Кэшировать результаты поиска"""
        key = f"search:{hash(query)}"
        return self.set(key, data, expire)


cache_service = CacheService()