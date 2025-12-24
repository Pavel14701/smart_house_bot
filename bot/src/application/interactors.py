from dataclasses import asdict

from aiogram import Bot
from aiogram.types import Voice
from faststream.rabbit import RabbitBroker

from application.dto import CommandDTO


class FirstTouchInteractor:
    def __init__(self) -> None:
        pass

    async def __call__(self, user_id: str | int, chat_id: str | int | None) -> None:
        pass 


class TextCommandInteractor:
    def __init__(self, broker):
        self._broker = broker

    async def __call__(self, user_id: str | int, message_id: str | int | None) -> None:
        dto = CommandDTO(
            user_id=str(user_id), 
            message_id=str(message_id) if message_id else None)
        await self._broker.publish(asdict(dto), queue="stt_command")


class VoiceCommandInteractor:
    def __init__(
        self, 
        broker: RabbitBroker, 
        bot: Bot
    ) -> None:
        self._broker = broker
        self._bot = bot

    async def __call__(
        self, 
        user_id: str | int, 
        message_id: str | int | None, 
        voice: Voice
    ) -> None:
        audio_bytes_io = await self._bot.download(voice)
        if audio_bytes_io is None:
            raise RuntimeError("Не удалось скачать голосовое сообщение")
        audio_bytes = audio_bytes_io.read()
        dto = CommandDTO(
            user_id=str(user_id), 
            message_id=str(message_id) if message_id else None)
        await self._broker.publish(
            {"id": dto.message_id, "user_id": dto.user_id, "content": audio_bytes},
            queue="stt_command",
        )
