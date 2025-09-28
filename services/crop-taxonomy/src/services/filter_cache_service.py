"""Performance optimization service for crop filtering system with multi-level caching."""

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    import redis.asyncio as redis
except ImportError:  # pragma: no cover - fallback when redis package unavailable
    redis = None

_filter_models_module = None
for _candidate in (
    'models.crop_filtering_models',
    'src.models.crop_filtering_models',
    '..models.crop_filtering_models'
):
    try:  # pragma: no cover - dynamic import resolution
        if _candidate.startswith('..'):
            _filter_models_module = import_module(_candidate, package=__package__)
        else:
            _filter_models_module = import_module(_candidate)
        break
    except ImportError:
        continue

if _filter_models_module is None:  # pragma: no cover - defensive guard
    raise ImportError('Unable to load crop filtering models for cache service')

CropSearchResponse = getattr(_filter_models_module, 'CropSearchResponse')

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Container for local cache entries."""

    payload: Dict[str, Any]
    expires_at: float
    created_at: float
    hit_count: int = 0


class InMemoryCacheLayer:
    """Simple in-memory cache with TTL and size limits."""

    def __init__(self, max_entries: int = 512):
        self.max_entries = max_entries
        self.storage: Dict[str, Dict[str, CacheEntry]] = {}
        self.hits = 0
        self.misses = 0

    def _namespace_bucket(self, namespace: str) -> Dict[str, CacheEntry]:
        bucket = self.storage.get(namespace)
        if bucket is None:
            bucket = {}
            self.storage[namespace] = bucket
        return bucket

    def get(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        bucket = self._namespace_bucket(namespace)
        entry = bucket.get(key)
        if entry is None:
            self.misses += 1
            return None
        current_time = time.time()
        if current_time >= entry.expires_at:
            try:
                del bucket[key]
            except KeyError:
                pass
            self.misses += 1
            return None
        entry.hit_count += 1
        self.hits += 1
        return entry.payload

    def set(self, namespace: str, key: str, payload: Dict[str, Any], ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            return
        bucket = self._namespace_bucket(namespace)
        expiration = time.time() + ttl_seconds
        entry = CacheEntry(payload=payload, expires_at=expiration, created_at=time.time())
        bucket[key] = entry
        self._enforce_limits(namespace, bucket)

    def delete(self, namespace: str, key: str) -> None:
        bucket = self.storage.get(namespace)
        if bucket is None:
            return
        try:
            del bucket[key]
        except KeyError:
            return

    def prune_expired(self) -> None:
        namespaces = list(self.storage.keys())
        index = 0
        while index < len(namespaces):
            namespace = namespaces[index]
            bucket = self.storage.get(namespace)
            if bucket is None:
                index += 1
                continue
            keys = list(bucket.keys())
            key_index = 0
            current_time = time.time()
            while key_index < len(keys):
                cache_key = keys[key_index]
                entry = bucket.get(cache_key)
                if entry is not None and current_time >= entry.expires_at:
                    try:
                        del bucket[cache_key]
                    except KeyError:
                        pass
                key_index += 1
            index += 1

    def get_stats(self) -> Dict[str, int]:
        stats: Dict[str, int] = {}
        stats['hits'] = self.hits
        stats['misses'] = self.misses
        total_entries = 0
        for namespace, bucket in self.storage.items():
            size = len(bucket)
            total_entries += size
        stats['entries'] = total_entries
        return stats

    def _enforce_limits(self, namespace: str, bucket: Dict[str, CacheEntry]) -> None:
        if len(bucket) <= self.max_entries:
            return
        # Remove oldest entries until the limit is satisfied
        while len(bucket) > self.max_entries:
            oldest_key = None
            oldest_time = None
            for key, entry in bucket.items():
                if oldest_time is None or entry.created_at < oldest_time:
                    oldest_key = key
                    oldest_time = entry.created_at
            if oldest_key is None:
                break
            try:
                del bucket[oldest_key]
            except KeyError:
                break
        # Clean up empty namespace buckets
        if len(bucket) == 0:
            try:
                del self.storage[namespace]
            except KeyError:
                pass


class FilterCacheService:
    """Redis-backed cache with local in-memory acceleration."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Any = None
        self.default_ttl = 3600
        self.local_cache = InMemoryCacheLayer(max_entries=1024)

    async def get_redis(self):
        if redis is None:
            raise RuntimeError("redis library is not installed")
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url)
        return self._redis

    # ------------------------------------------------------------------
    # Async crop search caching (used by async services)
    # ------------------------------------------------------------------

    async def get_search_result(self, request_id: str) -> Optional[CropSearchResponse]:
        cached_local = self.local_cache.get('crop_search', request_id)
        if cached_local is not None:
            try:
                return CropSearchResponse(**cached_local)
            except Exception as error:
                logger.debug("Failed to deserialize local cache for %s: %s", request_id, error)
        try:
            redis_client = await self.get_redis()
            cached_data = await redis_client.get(f"crop_search:{request_id}")
            if cached_data:
                try:
                    raw_data = json.loads(cached_data)
                    self.local_cache.set('crop_search', request_id, raw_data, self.default_ttl)
                    return CropSearchResponse(**raw_data)
                except Exception as error:
                    logger.warning("Failed to deserialize cached search result %s: %s", request_id, error)
        except Exception as error:
            logger.warning("Cache get error for search result %s: %s", request_id, error)
        return None

    async def cache_search_result(self, request_id: str, data: CropSearchResponse, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        if ttl <= 0:
            return
        try:
            payload = data.dict()
        except Exception:
            payload = json.loads(data.json())
        self.local_cache.set('crop_search', request_id, payload, ttl)
        try:
            redis_client = await self.get_redis()
            await redis_client.setex(f"crop_search:{request_id}", ttl, json.dumps(payload))
        except Exception as error:
            logger.warning("Cache set error for search result %s: %s", request_id, error)

    # ------------------------------------------------------------------
    # Synchronous helper utilities for filter engine and suggestions
    # ------------------------------------------------------------------

    def get_filter_combination(self, request_id: str) -> Optional[Dict[str, Any]]:
        cached_local = self.local_cache.get('filter_combination', request_id)
        if cached_local is not None:
            return cached_local
        remote_data = self._run_coroutine_blocking(self._get_remote_json('filter_combination', request_id))
        if remote_data is not None:
            self.local_cache.set('filter_combination', request_id, remote_data, self.default_ttl)
        return remote_data

    def cache_filter_combination(self, request_id: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self.local_cache.set('filter_combination', request_id, data, ttl)
        coroutine = self._set_remote_json('filter_combination', request_id, data, ttl)
        self._run_coroutine_background(coroutine)

    def get_suggestion_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        cached_local = self.local_cache.get('filter_suggestions', request_id)
        if cached_local is not None:
            return cached_local
        remote_data = self._run_coroutine_blocking(self._get_remote_json('filter_suggestions', request_id))
        if remote_data is not None:
            self.local_cache.set('filter_suggestions', request_id, remote_data, self.default_ttl)
        return remote_data

    def cache_suggestion_result(self, request_id: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self.local_cache.set('filter_suggestions', request_id, data, ttl)
        coroutine = self._set_remote_json('filter_suggestions', request_id, data, ttl)
        self._run_coroutine_background(coroutine)

    def cache_filter_options(self, location_hash: str, data: Dict[str, Any], ttl_seconds: int = 3600) -> None:
        self.local_cache.set('filter_options', location_hash, data, ttl_seconds)
        coroutine = self._set_remote_json('filter_options', location_hash, data, ttl_seconds)
        self._run_coroutine_background(coroutine)

    def get_filter_options(self, location_hash: str) -> Optional[Dict[str, Any]]:
        cached_local = self.local_cache.get('filter_options', location_hash)
        if cached_local is not None:
            return cached_local
        remote_data = self._run_coroutine_blocking(self._get_remote_json('filter_options', location_hash))
        if remote_data is not None:
            self.local_cache.set('filter_options', location_hash, remote_data, self.default_ttl)
        return remote_data

    def invalidate_search_cache(self, request_id: str) -> None:
        self.local_cache.delete('crop_search', request_id)
        coroutine = self._delete_remote_key(f"crop_search:{request_id}")
        self._run_coroutine_background(coroutine)

    def invalidate_filter_combination(self, request_id: str) -> None:
        self.local_cache.delete('filter_combination', request_id)
        coroutine = self._delete_remote_key(f"filter_combination:{request_id}")
        self._run_coroutine_background(coroutine)

    def invalidate_suggestion_cache(self, request_id: str) -> None:
        self.local_cache.delete('filter_suggestions', request_id)
        coroutine = self._delete_remote_key(f"filter_suggestions:{request_id}")
        self._run_coroutine_background(coroutine)

    def get_local_cache_stats(self) -> Dict[str, int]:
        return self.local_cache.get_stats()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_remote_json(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        try:
            redis_client = await self.get_redis()
            cached_data = await redis_client.get(f"{namespace}:{key}")
            if cached_data:
                try:
                    return json.loads(cached_data)
                except Exception as error:
                    logger.warning("Failed to load cached JSON for %s:%s: %s", namespace, key, error)
        except Exception as error:
            logger.warning("Remote cache get error for %s:%s: %s", namespace, key, error)
        return None

    async def _set_remote_json(self, namespace: str, key: str, data: Dict[str, Any], ttl: int) -> None:
        if ttl <= 0:
            return
        try:
            redis_client = await self.get_redis()
            await redis_client.setex(f"{namespace}:{key}", ttl, json.dumps(data))
        except Exception as error:
            logger.warning("Remote cache set error for %s:%s: %s", namespace, key, error)

    async def _delete_remote_key(self, redis_key: str) -> None:
        try:
            redis_client = await self.get_redis()
            await redis_client.delete(redis_key)
        except Exception as error:
            logger.warning("Remote cache delete error for %s: %s", redis_key, error)

    def _run_coroutine_blocking(self, coroutine) -> Optional[Dict[str, Any]]:
        if coroutine is None:
            return None
        result: Optional[Dict[str, Any]] = None
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(coroutine)
        except Exception as error:
            logger.debug("Background coroutine execution failed: %s", error)
        finally:
            loop.close()
        return result

    def _run_coroutine_background(self, coroutine) -> None:
        if coroutine is None:
            return

        def runner(task):
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(task)
            except Exception as error:
                logger.debug("Background cache coroutine error: %s", error)
            finally:
                loop.close()

        thread = threading.Thread(target=runner, args=(coroutine,), daemon=True)
        thread.start()


# Singleton instance
filter_cache_service = FilterCacheService()
