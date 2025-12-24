from typing import Any, AsyncIterable

from application import interfaces
from application.interactors import ProcessAudioEventInteractor
from config import Config
from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker, RabbitRouter
from infrastructure.adapters.redis import new_redis_client
from infrastructure.audio_convertator import PydubAudioConverter
from infrastructure.data_repo import DataRepository
from infrastructure.whisper_repo import WhisperAdapter
from redis.asyncio import Redis
from whisper import Whisper


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)
    broker = from_context(provides=RabbitBroker, scope=Scope.APP)
    model = from_context(provides=Whisper, scope=Scope.APP)
    controller = from_context(provides=RabbitRouter, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_redis_conn(self, config: Config) -> AsyncIterable[Redis[Any]]:
        conn = new_redis_client(config.redis)
        try:
            yield conn
        finally:
            await conn.close()

    whisper_gateway = provide(
        WhisperAdapter,
        scope=Scope.APP,
        provides=interfaces.ISpeechToTextAdapter
    )
    
    audio_convertator_gateway = provide(
        PydubAudioConverter,
        scope=Scope.APP,
        provides=interfaces.IAudioConvertator
    )

    exec_interactor = provide(
        source=ProcessAudioEventInteractor,
        scope=Scope.APP
    )

    data_repo = provide(
        DataRepository,
        scope=Scope.APP,
        provides=interfaces.IDataRepository
    )