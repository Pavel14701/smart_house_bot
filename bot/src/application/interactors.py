from domain.entities import AudioFileEntity, TelegramUserEntity, TextEventEntity

from application.dto import CommandDTO, CommandInputDTO, UserDTO
from application.interfaces import (
    MessageCacheProtocol,
    UnitOfWorkProtocol,
    UUIDGenerator,
)


class FirstTouchInteractor:
    def __init__(
        self,
        id_gen: UUIDGenerator,
        uow: UnitOfWorkProtocol
    ) -> None:
        self._id_gen = id_gen
        self._uow = uow

    async def __call__(self, dto: UserDTO) -> None:
        dm = TelegramUserEntity(
            id=self._id_gen(),
            telegram_id=dto.telegram_id,
            username=dto.username,
            first_name=dto.first_name,
            last_name=dto.last_name
        )
        await self._uow.users.add(dm)


class VoiceCommandInteractor:
    def __init__(
        self, 
        id_gen: UUIDGenerator, 
        msg_cache: MessageCacheProtocol
    ) -> None:
        self._id_gen = id_gen
        self._msg_cache = msg_cache

    async def __call__(self, dto: CommandInputDTO) -> CommandDTO:
        id = self._id_gen()
        if dto.voice:
            content = dto.voice.read()
            audio_file = AudioFileEntity(
                id=str(id),
                content=content,
                mimetype=dto.mime_type or "application/octet-stream",
            )
            await self._msg_cache.save_message(audio_file)
        else:
            raise ValueError("No voice in message")
        return CommandDTO(
            id=id,
            user_id=dto.user_id,
            chat_id=dto.chat_id,
            message_id=dto.message_id,
        )


class TextCommandInteractor:
    def __init__(self, id_gen: UUIDGenerator, msg_cache: MessageCacheProtocol) -> None:
        self._id_gen = id_gen
        self._msg_cache = msg_cache

    async def __call__(
        self,
        dto: CommandInputDTO
    ) -> CommandDTO:
        id = self._id_gen()
        if dto.text:
            text_event = TextEventEntity(id=str(id), text=dto.text)
            await self._msg_cache.save_message(text_event)
        else:
            raise ValueError("No text in message")
        return CommandDTO(
            id=id,
            user_id=dto.user_id,
            chat_id=dto.chat_id,
            message_id=dto.message_id,
        )

