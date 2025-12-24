import io
from typing import cast

from application.errors import AudioConversionError
from application.interfaces import IAudioConvertator
from domain.entities import AudioFile
from pydub import AudioSegment


class PydubAudioConverter(IAudioConvertator):
    async def to_wav(self, audio: AudioFile) -> AudioFile:
        if audio.mimetype == "audio/wav":
            return audio
        try:
            input_buffer: io.BytesIO = io.BytesIO(audio.content)
            fmt: str = audio.mimetype.split("/")[-1]
            segment = cast(AudioSegment, AudioSegment.from_file(
                file=input_buffer, 
                format=fmt
            ))
            output_buffer: io.BytesIO = io.BytesIO()
            segment.export(output_buffer, format="wav")
            return AudioFile(
                id=audio.id,
                content=output_buffer.getvalue(),
                filename=f"{audio.id}.wav",
                mimetype="audio/wav",
            )
        except Exception as e:
            raise AudioConversionError(
                f"Не удалось конвертировать {audio.mimetype} → wav: {e}"
            ) from e
