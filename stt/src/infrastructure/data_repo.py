import base64
import json
from typing import Any, cast

from application.errors import AudioNotFoundError
from application.interfaces import IDataRepository
from domain.entities import AudioFile, TextEvent
from redis.asyncio import Redis


class DataRepository(IDataRepository):
    def __init__(
        self, 
        client: Redis, 
    ) -> None:
        self._client = client

    async def get_message(self, audio_id: str) -> TextEvent | AudioFile:
        raw: bytes | None = cast(bytes | None, await self._client.get(audio_id))
        if raw is None:
            raise AudioNotFoundError(audio_id)
        payload: dict[str, Any] = json.loads(raw.decode("utf-8"))
        if "text" in payload:
            return TextEvent(
                id=audio_id,
                text=payload["text"],
            )
        return AudioFile(
            id=audio_id,
            content=base64.b64decode(payload["content"]),
            filename=payload["filename"],
            mimetype=payload.get("mimetype", "audio/wav"),
        )

    async def delete_audio(self, audio_id: str) -> None:
        await self._client.delete(f"audio:{audio_id}")

    async def save_text(self, text_event: TextEvent) -> str:
        await self._client.set(f"text:{text_event.id}", text_event.text)
        return text_event.id