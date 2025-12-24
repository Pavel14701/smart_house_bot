from typing import Protocol

from domain.entities import AudioFile, TextEvent


class IDataRepository(Protocol):
    async def get_message(self, audio_id: str) -> AudioFile | TextEvent:
        """Получить аудио по идентификатору"""
        ...

    async def delete_audio(self, audio_id: str) -> None:
        """Удалить аудио по идентификатору"""
        ...

    async def save_text(self, text_event: TextEvent) -> str:
        """Сохранить текстовое событие и вернуть его идентификатор"""
        ...


class ISpeechToTextAdapter(Protocol):
    async def transcribe(self, audio_bytes: bytes) -> str:
        """Преобразовать аудио в текст"""
        ...


class IAudioConvertator(Protocol):
    async def to_wav(self, audio: AudioFile) -> AudioFile:
        ...