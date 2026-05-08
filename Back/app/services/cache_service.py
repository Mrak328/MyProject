import json
import logging
from typing import Optional, Any
import redis
from redis.exceptions import ConnectionError, TimeoutError
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Сервис для работы с Redis кэшем"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            password=getattr(settings, 'REDIS_PASSWORD', None),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            retry_on_timeout=True,
            health_check_interval=30
        )

    def _safe_call(self, func, *args, **kwargs) -> Optional[Any]:
        """Безопасный вызов Redis с обработкой ошибок"""
        try:
            return func(*args, **kwargs)
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis connection error: {e}")
        except Exception as e:
            logger.error(f"Redis error: {e}")
        return None

    def ping(self) -> bool:
        """Проверка соединения"""
        return self._safe_call(self.redis_client.ping) or False

    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        value = self._safe_call(self.redis_client.get, key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value  # plain string
        return None

    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Сохранить значение в кэш"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, default=str)
        return bool(self._safe_call(self.redis_client.setex, key, expire, value))

    def delete(self, key: str) -> bool:
        """Удалить из кэша"""
        return bool(self._safe_call(self.redis_client.delete, key))

    def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        return bool(self._safe_call(self.redis_client.exists, key))

    def expire(self, key: str, seconds: int) -> bool:
        """Обновить TTL ключа"""
        return bool(self._safe_call(self.redis_client.expire, key, seconds))

    def incr(self, key: str) -> Optional[int]:
        """Инкремент счётчика"""
        return self._safe_call(self.redis_client.incr, key)

    def clear_pattern(self, pattern: str) -> int:
        """Удалить все ключи по шаблону"""
        keys = self._safe_call(self.redis_client.keys, pattern)
        if keys:
            result = self._safe_call(self.redis_client.delete, *keys)
            return result if result else 0
        return 0

    def flush(self) -> bool:
        """Очистить весь кэш (осторожно!)"""
        return bool(self._safe_call(self.redis_client.flushdb))

    # ============================================
    # СПЕЦИФИЧНЫЕ МЕТОДЫ
    # ============================================

    def cache_listing(self, listing_id: int, data: dict, expire: int = 3600) -> bool:
        """Кэшировать объявление"""
        return self.set(f"listing:{listing_id}", data, expire)

    def get_cached_listing(self, listing_id: int) -> Optional[dict]:
        """Получить кэшированное объявление"""
        return self.get(f"listing:{listing_id}")

    def invalidate_listing(self, listing_id: int) -> bool:
        """Инвалидировать кэш объявления"""
        return self.delete(f"listing:{listing_id}")

    def cache_search_results(self, query_params: dict, data: list, expire: int = 300) -> bool:
        """Кэшировать результаты поиска"""
        key = f"search:{hash(json.dumps(query_params, sort_keys=True))}"
        return self.set(key, data, expire)

    def get_cached_search(self, query_params: dict) -> Optional[list]:
        """Получить кэшированный поиск"""
        key = f"search:{hash(json.dumps(query_params, sort_keys=True))}"
        return self.get(key)

    def cache_popular_listings(self, data: list, expire: int = 600) -> bool:
        """Кэшировать популярные объявления"""
        return self.set("popular_listings", data, expire)

    def get_cached_popular_listings(self) -> Optional[list]:
        """Получить кэш популярных объявлений"""
        return self.get("popular_listings")

    def cache_dashboard(self, data: dict, expire: int = 300) -> bool:
        """Кэшировать дашборд"""
        return self.set("dashboard", data, expire)

    def get_cached_dashboard(self) -> Optional[dict]:
        """Получить кэш дашборда"""
        return self.get("dashboard")

    def increment_listing_views(self, listing_id: int) -> Optional[int]:
        """Увеличить счётчик просмотров объявления в кэше"""
        return self.incr(f"views:{listing_id}")


cache_service = CacheService()