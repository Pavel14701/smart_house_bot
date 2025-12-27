import asyncio

from aiogram import Bot, Dispatcher, Router
from config import Config
from dishka import make_async_container
from dishka.integrations.aiogram import (
    AiogramProvider,
)
from dishka.integrations.aiogram import (
    setup_dishka as aiogram_setup,
)
from dishka.integrations.faststream import FastStreamProvider
from dishka.integrations.faststream import setup_dishka as faststream_setup
from faststream.rabbit import RabbitBroker, RabbitRouter
from infrastructure.adapters.rabbit import new_broker
from ioc import BotProvider

bot_router = Router()
amqp_router = RabbitRouter()
config = Config()
bot = Bot(token=config.bot.token)
broker = new_broker(config.rabbit)
dp = Dispatcher()


async def main(
    config: Config,
    bot_router: Router,
    amqp_router: RabbitRouter,
    bot: Bot,
    broker: RabbitBroker,
    dp: Dispatcher
) -> None:
    dp.include_router(bot_router)
    container = make_async_container(
        BotProvider(),
        AiogramProvider(),
        FastStreamProvider(),
        context={
            Config: config,
            RabbitBroker: broker,
            Router: bot_router,
            RabbitRouter: amqp_router,
            Bot: bot
        },
    )
    aiogram_setup(container=container, router=dp, auto_inject=True)
    faststream_setup(container=container, broker=broker, auto_inject=True)
    try:
        await broker.start()
        await dp.start_polling(bot)
    finally:
        await broker.stop()
        await container.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main(
        config=config, 
        bot_router=bot_router,
        amqp_router=amqp_router,
        bot=bot,
        broker=broker,
        dp=dp
    ))
