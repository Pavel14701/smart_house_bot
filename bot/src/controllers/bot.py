from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Chat, Message, User
from application.interactors import (
    FirstTouchInteractor,
    TextCommandInteractor,
    VoiceCommandInteractor,
)
from dishka.integrations.aiogram import FromDishka, inject

from controllers.states import CommandState


class BotControllers:
    def __init__(
        self,
        router: Router
    ) -> None:
        self._router = router
        self._router.message(Command("start"))(self.start_handler)
        self._router.message(CommandState.waiting_for_command)(self.command_handler)

    @inject
    async def start_handler(
        self,
        message: Message, 
        user: FromDishka[User],
        chat: FromDishka[Chat | None],
        interactor: FromDishka[FirstTouchInteractor],
        state: FSMContext) -> None:
        chat_id = chat.id if chat else None
        await interactor(user.id, chat_id)
        await message.answer("Отправь команду текстом или голосом 🎤")
        await state.set_state(CommandState.waiting_for_command)

    @inject
    async def command_handler(
        self,
        message: Message,
        user: FromDishka[User],
        chat: FromDishka[Chat | None],
        voice_interactor: FromDishka[VoiceCommandInteractor],
        text_interactor: FromDishka[TextCommandInteractor],
        state: FSMContext
    ) -> None:
        if message.voice:
            chat_id = chat.id if chat else None
            await voice_interactor(
                user.id , chat_id , message.voice
            )
            await message.answer("Голосовая команда отправлена ✅")
        elif message.text:
            await text_interactor(user.id, message.message_id)
            await message.answer("Текстовая команда отправлена ✅")
        else:
            await message.answer("Поддерживаются только текст и голос 🎤")