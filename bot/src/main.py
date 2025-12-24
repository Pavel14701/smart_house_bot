import asyncio

from aiogram import Bot, Dispatcher, Router
from config import Config
from dishka import make_async_container
from dishka.integrations.aiogram import (
    AiogramProvider,
    setup_dishka,
)
from faststream.rabbit import RabbitBroker
from infrastructure.adapters.rabbit import new_broker
from ioc import BotProvider


router = Router()
config = Config()


async def main(
    config: Config, 
    router: Router, 
) -> None:
    bot = Bot(token=config.bot.token)
    broker = new_broker(config.rabbit)
    dp = Dispatcher()
    dp.include_router(router)
    container = make_async_container(
        BotProvider(),
        AiogramProvider(),
        context={
            Config: config,
            RabbitBroker: broker,
            Router: router
        }
    )
    setup_dishka(container=container, router=dp)
    try:
        await dp.start_polling(bot)
    finally:
        await container.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main(config, router))
