from typing import Any, AsyncIterable
from uuid import UUID, uuid7  # type: ignore[attr-defined]

from aiogram import Bot, Router
from aiogram.types import Chat, Message, User
from application import interfaces
from config import Config
from controllers.middleware import DomainErrorMiddleware
from dishka import AnyOf, Provider, Scope, from_context, provide
from dishka.integrations.aiogram import AiogramMiddlewareData
from faststream.rabbit import RabbitBroker, RabbitRouter
from infrastructure.adapters.postgres import new_session_maker
from infrastructure.adapters.redis import new_redis_client
from infrastructure.adapters.uow import UnitOfWork
from infrastructure.repositories.home import HomeRepositorySQL
from infrastructure.repositories.home_user_role import HomeUserRoleRepositorySQL
from infrastructure.repositories.message_cache import MessageCacheRepository
from infrastructure.repositories.smart_device import SmartDeviceRepositorySQL
from infrastructure.repositories.user import TelegramUserRepositorySQL
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class BotProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)
    broker = from_context(provides=RabbitBroker, scope=Scope.APP)
    bot_router = from_context(provides=Router, scope=Scope.APP)
    bot = from_context(provides=Bot, scope=Scope.APP)
    amqp_router = from_context(provides=RabbitRouter, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_chat(
            self,
            middleware_data: AiogramMiddlewareData,
    ) -> Chat | None:
        return middleware_data.get("chat")

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

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AnyOf[AsyncSession, interfaces.SessionProtocol]]:
        async with session_maker() as session:
            yield session

    @provide(interfaces.UUIDGenerator, scope=Scope.APP)
    def get_uuid(self) -> UUID:
        return uuid7()

    message_cache_repo = provide(
        source=MessageCacheRepository,
        scope=Scope.APP,
        provides=interfaces.MessageCacheProtocol
    )

    @provide(interfaces.TelegramUserRepositoryProtocol, scope=Scope.REQUEST)
    def get_user_repo(self) -> type[TelegramUserRepositorySQL]:
        return TelegramUserRepositorySQL

    @provide(interfaces.HomeUserRoleRepositoryProtocol, scope=Scope.REQUEST)
    def get_home_user_role_repo(self) -> type[HomeUserRoleRepositorySQL]:
        return HomeUserRoleRepositorySQL

    @provide(interfaces.HomeRepositoryProtocol, scope=Scope.REQUEST)
    def get_home_repo(self) -> type[HomeRepositorySQL]:
        return HomeRepositorySQL
    
    @provide(interfaces.SmartDeviceRepositoryProtocol, scope=Scope.REQUEST)
    def get_smart_device_repo(self) -> type[SmartDeviceRepositorySQL]:
        return SmartDeviceRepositorySQL

    uow_adapter = provide(
        source=UnitOfWork, 
        scope=Scope.REQUEST, 
        provides=interfaces.UnitOfWorkProtocol
    )

    error_midleware = provide(
        source=DomainErrorMiddleware,
        scope=Scope.APP
    )