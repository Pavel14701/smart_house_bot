from dishka import make_async_container
from dishka.integrations.faststream import setup_dishka  # type: ignore
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitRouter
import whisper

from .config import Config
from .infrastructure.adapters.rabbit import new_broker
from .ioc import AppProvider


config = Config()
model = whisper.load_model("base")
controller = RabbitRouter()


def get_faststream_app(
    config: Config, 
    model: whisper.Whisper,
    controller: RabbitRouter
) -> FastStream:
    broker = new_broker(config.rabbit)
    container = make_async_container(
        AppProvider(),
        context={
            Config: config, 
            RabbitBroker: broker,
            whisper.Whisper: model,
            RabbitRouter: controller
        }
    )
    faststream_app = FastStream(broker)
    setup_dishka(
        container=container, 
        app=faststream_app, 
        auto_inject=True
    )
    broker.include_router(controller)
    return faststream_app


if __name__ == "__main__":
    import asyncio
    app = get_faststream_app(config, model, controller)
    asyncio.run(app.run())