import tempfile
from typing import Any, cast

from application.interfaces import ISpeechToTextAdapter
import whisper


class WhisperAdapter(ISpeechToTextAdapter):
    def __init__(self, model: whisper.Whisper) -> None:
        self._model = model

    async def transcribe(self, audio_bytes: bytes) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            result: dict[str, Any] = self._model.transcribe(tmp.name) 
            return cast(str, result["text"])