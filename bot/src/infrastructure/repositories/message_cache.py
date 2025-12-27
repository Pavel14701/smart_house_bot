import base64
import json
from typing import Any

from application.interfaces import MessageCacheProtocol
from domain.entities import AudioFileEntity, TextEventEntity
from domain.errors import DomainError
from redis.asyncio import Redis


class MessageCacheRepository(MessageCacheProtocol):
    """
    Small wrapper that provides save method for audio messages in cache.
    Assumes self._client implements async get/set interface 
    similar to aioredis or redis.asyncio.
    """

    def __init__(self, client: Redis) -> None:
        """
        client: async redis-like client with `get(key)` 
        and `set(key, value, ex=ttl)` methods.
        """
        self._client = client

    async def save_message(
        self,
        message: TextEventEntity | AudioFileEntity,
        *,
        ttl: int | None = None,
    ) -> None:
        """
        Save a TextEvent or AudioFile to cache.

        Parameters
        ----------
        message:
            TextEvent or AudioFile instance to store.
        ttl:
            Optional time-to-live in seconds. If None, the key will not expire.

        Raises
        ------
        DomainError
            If cache operation fails.
        """
        key = f"audio:{message.id}"
        if isinstance(message, TextEventEntity):
            payload: dict[str, Any] = {"text": message.text}
        elif isinstance(message, AudioFileEntity):
            content_b64 = base64.b64encode(message.content).decode("ascii")
            payload = {
                "content": content_b64,
                "mimetype": message.mimetype,
            }
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        try:
            if ttl is None:
                await self._client.set(key, raw)
            else:
                await self._client.set(key, raw, ex=ttl)
        except Exception as exc:
            raise DomainError("Failed to save message to cache") from exc