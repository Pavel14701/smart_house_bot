from typing import Any, AsyncIterable
from uuid import UUID, uuid7  # type: ignore[attr-defined]

from aiogram import Router
from aiogram.types import Chat, Message, User
from application import interfaces
from config import Config
from dishka import Provider, Scope, from_context, provide
from dishka.integrations.aiogram import AiogramMiddlewareData
from faststream.rabbit import RabbitBroker
from infrastructure.adapters.redis import new_redis_client
from redis.asyncio import Redis


class BotProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)
    broker = from_context(provides=RabbitBroker, scope=Scope.APP)
    router = from_context(provides=Router, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_chat(
            self,
            middleware_data: AiogramMiddlewareData,
    ) -> Chat | None:
        return middleware_data.get("bot")

    @provide(scope=Scope.REQUEST) 
    async def get_user(self, message: Message) -> User | None: 
        return message.from_user

    @provide(scope=Scope.REQUEST)
    async def get_redis_conn(self, config: Config) -> AsyncIterable[Redis[Any]]:
        conn = new_redis_client(config.redis)
        try:
            yield conn
        finally:
            await conn.close()

    @provide(interfaces.UUIDGenerator, scope=Scope.APP)
    def get_uuid(self) -> UUID:
        return uuid7()