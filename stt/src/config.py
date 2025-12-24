import os

from pydantic import BaseModel, Field


class RabbitMQConfig(BaseModel):
    host: str = Field(alias="RABBITMQ_HOST")
    port: int = Field(alias="RABBITMQ_PORT")
    login: str = Field(alias="RABBITMQ_USER")
    password: str = Field(alias="RABBITMQ_PASSWORD")
    vhost: str = Field(alias="RABBITMQ_VHOST")


class RedisConfig(BaseModel):
    host: str = Field(alias="REDIS_HOST")
    port: int = Field(alias="REDIS_PORT")
    db: int = Field(alias="REDIS_ACCOUNT_EVENTS_DB")
    password: str = Field(alias="REDIS_PASSWORD")


class Config(BaseModel):
    rabbit: RabbitMQConfig = Field(
        default_factory=lambda: RabbitMQConfig.model_validate(os.environ)
    )
    redis: RedisConfig = Field(
        default_factory=lambda: RedisConfig.model_validate(os.environ)
    )
