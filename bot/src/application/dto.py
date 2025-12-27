from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserDTO:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None


@dataclass(frozen=True, slots=True)
class CommandDTO:
    id: str | UUID
    user_id: int
    message_id: int
    chat_id: int | None = None


@dataclass(frozen=True, slots=True)
class CommandInputDTO:
    user_id: int
    message_id: int
    chat_id: int | None = None
    text: str | None = None
    voice: BinaryIO | None = None
    mime_type: str | None = None
