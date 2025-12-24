class AudioConversionError(Exception):
    """Ошибка конвертации аудио."""


class AudioNotFoundError(Exception):
    """Аудио с указанным идентификатором не найдено."""
    def __init__(self, audio_id: str) -> None:
        super().__init__(f"Audio {audio_id} not found")
        self.audio_id = audio_id
