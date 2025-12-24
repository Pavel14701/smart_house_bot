from domain.entities import TextEvent

from .interfaces import (
    IAudioConvertator,
    IDataRepository,
    ISpeechToTextAdapter,
)


class ProcessAudioEventInteractor:
    def __init__(
        self,
        audio_repo: IDataRepository,
        stt: ISpeechToTextAdapter,
        converter: IAudioConvertator,
    ) -> None:
        self._audio_repo = audio_repo
        self._stt = stt
        self._converter = converter

    async def __call__(self, event_id: str) -> TextEvent:
        audio = await self._audio_repo.get_message(event_id)
        if isinstance(audio, TextEvent):
            return audio
        audio = await self._converter.to_wav(audio)
        text: str = await self._stt.transcribe(audio.content)
        text_event = TextEvent(id=event_id, text=text)
        await self._audio_repo.save_text(text_event)
        await self._audio_repo.delete_audio(text_event.id)
        return text_event
