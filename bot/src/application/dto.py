from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandDTO:
    user_id: str
    message_id: str | None
