from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandDTO:
    user_id: str
    message_id: str
    chat_id: str | None = None


@dataclass(frozen=True, slots=True)
class SuccessEventDTO:
    user_id: str
    message_id: str
    text: str


@dataclass(frozen=True, slots=True)
class ErrorEventDTO:
    user_id: str
    message_id: str
    reason: str
