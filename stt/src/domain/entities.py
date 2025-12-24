from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AudioFile:
    id: str
    content: bytes
    filename: str
    mimetype: str = "audio/wav"


@dataclass(frozen=True, slots=True)
class TextEvent:
    id: str
    text: str
