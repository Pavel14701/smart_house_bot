from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from domain.errors import DomainError


class DomainErrorMiddleware(BaseMiddleware):
    """
    Ловит DomainError и отправляет текст ошибки пользователю, если событие — Message.
    Для других типов событий просто пропускает дальше.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except (DomainError, ValueError, RuntimeError) as exc:
            if isinstance(event, Message):
                await event.answer(str(exc))
                return None
            raise
