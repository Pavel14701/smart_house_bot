from dataclasses import asdict

from application.dto import CommandDTO, ErrorEventDTO, SuccessEventDTO
from application.errors import AudioNotFoundError
from application.interactors import ProcessAudioEventInteractor
from dishka.integrations.faststream import FromDishka, inject
from faststream.rabbit import RabbitBroker, RabbitRouter


class AudioController:
    def __init__(self, router: RabbitRouter, broker: RabbitBroker) -> None:
        self.router = router
        self.broker = broker
        router.subscriber("stt_command")(self.process_audio)

    @inject
    async def process_audio(
        self,
        dto: CommandDTO,
        interactor: FromDishka[ProcessAudioEventInteractor],
    ) -> None:
        try:
            event = await interactor(dto.message_id)
            await self.publish_success(
                SuccessEventDTO(
                    user_id=dto.user_id, 
                    message_id=dto.message_id, 
                    text=event.text
                )
            )
        except AudioNotFoundError as e:
            await self.publish_error(
                ErrorEventDTO(
                    user_id=dto.user_id, 
                    message_id=dto.message_id, 
                    reason=str(e)
                )
            )
        except Exception as e:
            await self.publish_error(
                ErrorEventDTO(
                    user_id=dto.user_id, 
                    message_id=dto.message_id, 
                    reason=f"Internal error: {e}"
                )
            )

    async def publish_success(self, dto: SuccessEventDTO) -> None:
        await self.broker.publish(asdict(dto), queue="nlu_command")

    async def publish_error(self, dto: ErrorEventDTO) -> None:
        await self.broker.publish(asdict(dto), queue="error_queue")
