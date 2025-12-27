from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Chat, Message, User
from application.dto import CommandInputDTO, UserDTO
from application.interactors import (
    FirstTouchInteractor,
    TextCommandInteractor,
    VoiceCommandInteractor,
)
from dishka import FromDishka
from faststream.rabbit import RabbitRouter

from controllers.middleware import DomainErrorMiddleware
from controllers.states import CommandState


class BotControllers:
    def __init__(
        self,
        amqp_router: RabbitRouter,
        bot_router: Router,
        bot: Bot,
        midleware: DomainErrorMiddleware, 
    ) -> None:
        self._bot = bot
        self._bot_router = bot_router
        self._amqp_router = amqp_router
        self._bot_router.message(Command("start"))(self.start_handler)
        self._bot_router.message(StateFilter(CommandState.waiting_for_command))(self.command_handler)
        self._bot_router.message.middleware(midleware)
        self._amqp_router.publisher("stt_command")(self.command_handler)

    async def start_handler(
        self,
        message: Message, 
        user: FromDishka[User],
        chat: FromDishka[Chat | None],
        interactor: FromDishka[FirstTouchInteractor],
        state: FSMContext) -> None:
        await interactor(UserDTO(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        ))
        await message.answer("Отправь команду текстом или голосом 🎤")
        await state.set_state(CommandState.waiting_for_command)

    async def command_handler(
        self,
        message: Message,
        user: FromDishka[User],
        chat: FromDishka[Chat | None],
        voice_interactor: FromDishka[VoiceCommandInteractor],
        text_interactor: FromDishka[TextCommandInteractor],
        state: FSMContext,
    ) -> None:
        chat_id = chat.id if chat else None
        user_id = user.id if user else None
        message_id = message.message_id
        if user_id is None:
            await message.answer("Unknown sender")
            return
        if message.voice:
            mime_type = message.voice.mime_type
            audio_bytes_io = await self._bot.download(message.voice)
            if audio_bytes_io is None:
                raise RuntimeError("Failed to download voice message")
            await voice_interactor(CommandInputDTO(
                user_id, message_id, chat_id, 
                voice=audio_bytes_io, mime_type=mime_type
            ))
            await message.answer("Голосовая команда отправлена ✅")
        elif text := message.text:
            await text_interactor(CommandInputDTO(
                user_id, message_id, chat_id, text=text
            ))
            await message.answer("Текстовая команда отправлена ✅")
        else:
            await message.answer("Only text and voice are supported 🎤")


